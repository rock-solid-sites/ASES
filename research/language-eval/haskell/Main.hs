{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE BangPatterns #-}
-- Conventional Haskell baseline, deliberately not a state-machine implementation.
-- Research only: no operational admissions or provider integration.
import Control.Monad (unless)
import Data.List (foldl')
import Data.Aeson (FromJSON(..), Value, eitherDecode, encode, object, withObject, (.:), (.=))
import Data.Aeson.Key (Key)
import qualified Data.Aeson.Key as K
import qualified Data.Aeson.KeyMap as KM
import Data.Aeson.Types (Object, Parser)
import qualified Data.ByteString.Lazy.Char8 as BL
import qualified Data.Text as T
import System.Exit (die)
import System.Environment (getArgs)
import Text.Read (readMaybe)
import GHC.Clock (getMonotonicTimeNSec)

data Case = Case
  { ident :: T.Text
  , fundingMode :: T.Text
  , active :: Bool
  , verified :: Bool
  , evidenceCurrent :: Bool
  , priceKnown :: Bool
  , capacity :: Integer
  , reserved :: Integer
  , requested :: Integer
  , usage :: Integer
  , included :: Integer
  , rate :: Integer
  , wallet :: Integer
  , walletFloor :: Integer
  , liability :: Integer
  , spendCap :: Integer
  , paidOptIn :: Bool
  }

maxI64, minI64 :: Integer
maxI64 = 9223372036854775807
minI64 = -9223372036854775808

-- Match Rust's i64 JSON wire contract. Haskell Integer is intentionally used
-- for checked arithmetic AFTER bounded field parsing, avoiding overflow.
bounded :: Object -> Key -> Parser Integer
bounded o k = do
  n <- o .: k
  if n >= minI64 && n <= maxI64
    then pure n
    else fail "integer outside signed 64-bit wire range"

instance FromJSON Case where
  parseJSON = withObject "Case" $ \o -> do
    let known = [ "id", "mode", "active", "verified", "evidence_current",
                  "price_known", "capacity", "reserved", "requested", "usage",
                  "included", "rate", "wallet", "wallet_floor", "liability",
                  "spend_cap", "paid_opt_in" ] :: [T.Text]
    unless (all (`elem` known) (map K.toText (KM.keys o))) $
      fail "unknown Case field"
    Case
      <$> o .: "id"
      <*> o .: "mode"
      <*> o .: "active"
      <*> o .: "verified"
      <*> o .: "evidence_current"
      <*> o .: "price_known"
      <*> bounded o "capacity"
      <*> bounded o "reserved"
      <*> bounded o "requested"
      <*> bounded o "usage"
      <*> bounded o "included"
      <*> bounded o "rate"
      <*> bounded o "wallet"
      <*> bounded o "wallet_floor"
      <*> bounded o "liability"
      <*> bounded o "spend_cap"
      <*> o .: "paid_opt_in"

-- A strict, non-JSON decision representation for the computation-only probe.
-- The normal wire mode serializes the identical verdict via asValue.
data Verdict = Verdict
  { vAccepted :: !Bool
  , vReason :: !T.Text
  , vCharge :: !Integer
  }

outcome :: T.Text -> Integer -> Verdict
outcome reason charge = Verdict (reason == "admitted") reason charge

asValue :: Case -> Verdict -> Value
asValue c v = object
  [ "id" .= ident c
  , "accepted" .= vAccepted v
  , "reason" .= vReason v
  , "charge_cents" .= vCharge v
  ]

decide :: Case -> Verdict
decide c = decideWithUsage c (usage c)

decideWithUsage :: Case -> Integer -> Verdict
decideWithUsage c currentUsage
  | any (< 0) [capacity c, reserved c, requested c, currentUsage,
               included c, rate c, wallet c, walletFloor c,
               liability c, spendCap c] || requested c == 0 = deny "invalid-input"
  | fundingMode c `notElem` ["free", "subscription", "prepaid", "postpaid"] = deny "invalid-input"
  | not (active c) = deny "inactive"
  | not (verified c) = deny "unverified"
  | not (evidenceCurrent c) = deny "stale-evidence"
  | not (priceKnown c) = deny "unknown-price"
  | reserved c > capacity c || requested c > capacity c - reserved c = deny "capacity-exceeded"
  | charge > maxI64 = deny "arithmetic-overflow"
  | charge > 0 && not (paidOptIn c) = deny "paid-opt-in-required"
  | fundingMode c == "prepaid" && (wallet c < walletFloor c
      || charge > wallet c - walletFloor c) = deny "wallet-floor-exceeded"
  | fundingMode c /= "prepaid" && (liability c > spendCap c
      || charge > spendCap c - liability c) = deny "spend-cap-exceeded"
  | otherwise = outcome "admitted" charge
  where
    deny reason = outcome reason 0
    billable = if fundingMode c == "free" || fundingMode c == "subscription"
               then max 0 (currentUsage - included c)
               else currentUsage
    charge = billable * rate c

reasonCode :: T.Text -> Integer
reasonCode "admitted" = 0
reasonCode "invalid-input" = 1
reasonCode "inactive" = 2
reasonCode "unverified" = 3
reasonCode "stale-evidence" = 4
reasonCode "unknown-price" = 5
reasonCode "capacity-exceeded" = 6
reasonCode "arithmetic-overflow" = 7
reasonCode "paid-opt-in-required" = 8
reasonCode "wallet-floor-exceeded" = 9
reasonCode "spend-cap-exceeded" = 10
reasonCode _ = 99

-- Time repeated admission decisions after the JSON input is decoded, without
-- constructing or encoding individual JSON output objects in the timed loop.
-- A changing usage offset prevents pure-function result sharing between passes.
benchCore :: [Case] -> Integer -> IO ()
benchCore cs passes = do
  started <- getMonotonicTimeNSec
  let loop !roundNo !accepted !charges !reasons
        | roundNo >= passes = (accepted, charges, reasons)
        | otherwise =
            let (!a, !ch, !r) = foldl' (step roundNo) (accepted, charges, reasons) cs
            in loop (roundNo + 1) a ch r
      step roundNo (!accepted, !charges, !reasons) c =
        let currentUsage = if usage c <= maxI64 - 16
                           then usage c + (roundNo `mod` 17)
                           else usage c
            !v = decideWithUsage c currentUsage
            !nextAccepted = accepted + (if vAccepted v then 1 else 0)
            !nextCharges = charges + vCharge v
            !nextReasons = reasons + reasonCode (vReason v)
        in (nextAccepted, nextCharges, nextReasons)
      (!a, !ch, !r) = loop 0 (0 :: Integer) (0 :: Integer) (0 :: Integer)
  a `seq` ch `seq` r `seq` pure ()
  finished <- getMonotonicTimeNSec
  BL.putStrLn (encode (object
    [ "accepted_count" .= a
    , "charge_sum" .= ch
    , "reason_sum" .= r
    , "evaluations" .= (fromIntegral (length cs) * passes :: Integer)
    , "core_ns" .= (toInteger finished - toInteger started)
    ]))

main :: IO ()
main = do
  args <- getArgs
  input <- BL.getContents
  case eitherDecode input :: Either String [Case] of
    Left problem -> die problem
    Right cases -> case args of
      [] -> BL.putStrLn (encode (map (\c -> asValue c (decide c)) cases))
      ["--bench-core", count] ->
        case readMaybe count :: Maybe Integer of
          Just passes | passes >= 1 && passes <= 10000 -> benchCore cases passes
          _ -> die "--bench-core passes must be 1..=10000"
      _ -> die "usage: ases-admit-hs [--bench-core PASSES]"
