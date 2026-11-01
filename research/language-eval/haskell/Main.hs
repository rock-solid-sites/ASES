{-# LANGUAGE OverloadedStrings #-}
-- Conventional Haskell baseline, deliberately not a state-machine implementation.
-- Research only: no operational admissions or provider integration.
import Control.Monad (unless)
import Data.Aeson (FromJSON(..), Value, eitherDecode, encode, object, withObject, (.:), (.=))
import Data.Aeson.Key (Key)
import qualified Data.Aeson.Key as K
import qualified Data.Aeson.KeyMap as KM
import Data.Aeson.Types (Object, Parser)
import qualified Data.ByteString.Lazy.Char8 as BL
import qualified Data.Text as T
import System.Exit (die)

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

outcome :: Case -> T.Text -> Integer -> Value
outcome c reason charge = object
  [ "id" .= ident c
  , "accepted" .= (reason == "admitted")
  , "reason" .= reason
  , "charge_cents" .= charge
  ]

decide :: Case -> Value
decide c
  | any (< 0) [capacity c, reserved c, requested c, usage c,
               included c, rate c, wallet c, walletFloor c,
               liability c, spendCap c] || requested c == 0 = deny "invalid-input"
  | fundingMode c `notElem` ["free", "subscription", "prepaid", "postpaid"] = deny "invalid-input"
  | not (active c) = deny "inactive"
  | not (verified c) = deny "unverified"
  | not (evidenceCurrent c) = deny "stale-evidence"
  | not (priceKnown c) = deny "unknown-price"
  | reserved c > capacity c || requested c > capacity c - reserved c = deny "capacity-exceeded"
  | charge > 9223372036854775807 = deny "arithmetic-overflow"
  | charge > 0 && not (paidOptIn c) = deny "paid-opt-in-required"
  | fundingMode c == "prepaid" && (wallet c < walletFloor c
      || charge > wallet c - walletFloor c) = deny "wallet-floor-exceeded"
  | fundingMode c /= "prepaid" && (liability c > spendCap c
      || charge > spendCap c - liability c) = deny "spend-cap-exceeded"
  | otherwise = outcome c "admitted" charge
  where
    deny reason = outcome c reason 0
    billable = if fundingMode c == "free" || fundingMode c == "subscription"
               then max 0 (usage c - included c)
               else usage c
    charge = billable * rate c

main :: IO ()
main = do
  input <- BL.getContents
  case eitherDecode input :: Either String [Case] of
    Left problem -> die problem
    Right cases -> BL.putStrLn (encode (map decide cases))
