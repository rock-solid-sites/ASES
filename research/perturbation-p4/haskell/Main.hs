{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE BangPatterns #-}
-- P4 minimal in-memory stateful research implementation.
-- Stale-snapshot is intentionally faulty; no provider/payment integration.
import Control.Concurrent (forkIO, threadDelay)
import Control.Concurrent.Chan (newChan, readChan, writeChan)
import Control.Concurrent.MVar (newEmptyMVar, newMVar, readMVar, putMVar, modifyMVar)
import Control.Monad (forM_, replicateM)
import Data.Aeson (FromJSON(..), eitherDecode, encode, object, withObject, (.:), (.=))
import qualified Data.ByteString.Lazy.Char8 as BL
import qualified Data.Text as T
import Data.List (sortOn)
import Data.Maybe (fromMaybe)
import GHC.Clock (getMonotonicTimeNSec)
import System.Environment (getArgs)
import System.Exit (die)
import Text.Read (readMaybe)

data Request = Request
  { requestId :: !T.Text
  , requestUnits :: !Integer
  , requestCharge :: !Integer
  , requestOptIn :: !Bool
  }
instance FromJSON Request where
  parseJSON = withObject "Request" $ \o ->
    Request <$> o .: "id" <*> o .: "units" <*> o .: "charge_cents" <*> o .: "paid_opt_in"

data Trial = Trial
  { capacity :: !Integer
  , spendCap :: !Integer
  , requests :: ![Request]
  }
instance FromJSON Trial where
  parseJSON = withObject "Trial" $ \o ->
    Trial <$> o .: "capacity" <*> o .: "spend_cap_cents" <*> o .: "requests"

data ReserveState = ReserveState
  { totalReserved :: !Integer
  , totalCharged :: !Integer
  , committedIds :: ![T.Text]
  , totalAccepted :: !Int
  }
initial :: ReserveState
initial = ReserveState 0 0 [] 0

allowed :: Trial -> Request -> ReserveState -> Bool
allowed trial req st =
  requestUnits req > 0
  && requestCharge req >= 0
  && (requestCharge req == 0 || requestOptIn req)
  && notElem (requestId req) (committedIds st)
  && totalReserved st + requestUnits req <= capacity trial
  && totalCharged st + requestCharge req <= spendCap trial

apply :: Request -> ReserveState -> ReserveState
apply req st = ReserveState
  (totalReserved st + requestUnits req)
  (totalCharged st + requestCharge req)
  (requestId req : committedIds st)
  (totalAccepted st + 1)

main :: IO ()
main = do
  args <- getArgs
  (stale, delayUs) <- case args of
    ["--mode", "safe", "--delay-us", n] ->
      case readMaybe n of
        Just x | x >= 0 && x <= (10000 :: Int) -> pure (False, x)
        _ -> die "delay must be between 0 and 10000us"
    ["--mode", "stale", "--delay-us", n] ->
      case readMaybe n of
        Just x | x >= 0 && x <= (10000 :: Int) -> pure (True, x)
        _ -> die "delay must be between 0 and 10000us"
    _ -> die "usage: p4 --mode safe|stale --delay-us N"
  bytes <- BL.getContents
  trial <- case eitherDecode bytes of
    Left err -> die err
    Right x -> pure x
  if null (requests trial) || length (requests trial) > 16
     || capacity trial < 0 || spendCap trial < 0
    then die "invalid bounded trial" else pure ()
  begin <- getMonotonicTimeNSec
  state <- newMVar initial
  gate <- newEmptyMVar
  ready <- newChan
  results <- newChan
  let count = length (requests trial)
  forM_ (zip [0 :: Int ..] (requests trial)) $ \(idx, req) -> do
    _ <- forkIO $ do
      snapshot <- if stale then Just <$> readMVar state else pure Nothing
      writeChan ready idx
      readMVar gate
      answer <- modifyMVar state $ \current -> do
        startedPause <- getMonotonicTimeNSec
        if delayUs > 0 then threadDelay delayUs else pure ()
        endPause <- getMonotonicTimeNSec
        let viewed = fromMaybe current snapshot
            !admitted = allowed trial req viewed
            !changed = if admitted then apply req current else current
            !pauseUs = (endPause - startedPause) `div` 1000
        pure (changed, (idx, admitted, pauseUs))
      writeChan results answer
    pure ()
  _ <- replicateM count (readChan ready)
  putMVar gate ()
  outcomes <- replicateM count (readChan results)
  finished <- getMonotonicTimeNSec
  final <- readMVar state
  let sorted = sortOn (\(idx, _, _) -> idx) outcomes
      pauses = [micros | (_, _, micros) <- outcomes]
  BL.putStrLn $ encode $ object
    [ "accepted_count" .= totalAccepted final
    , "rejected_count" .= (count - totalAccepted final)
    , "reserved" .= totalReserved final
    , "charged_cents" .= totalCharged final
    , "unique_commit_count" .= length (committedIds final)
    , "workers_reached_barrier" .= count
    , "per_request_accepted" .= [b | (_, b, _) <- sorted]
    , "measured_delay_us_min" .= minimum pauses
    , "measured_delay_us_sum" .= sum pauses
    , "elapsed_us" .= ((finished - begin) `div` 1000)
    ]
