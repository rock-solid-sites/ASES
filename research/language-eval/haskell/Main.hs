{-# LANGUAGE OverloadedStrings #-}
-- Conventional Haskell baseline, deliberately not a state-machine implementation.
-- Research only: no operational admissions or provider integration.
import Data.Aeson (FromJSON(..), Value, eitherDecode, encode, object, withObject, (.:), (.=))
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

instance FromJSON Case where
  parseJSON = withObject "Case" $ \o -> Case
    <$> o .: "id"
    <*> o .: "mode"
    <*> o .: "active"
    <*> o .: "verified"
    <*> o .: "evidence_current"
    <*> o .: "price_known"
    <*> o .: "capacity"
    <*> o .: "reserved"
    <*> o .: "requested"
    <*> o .: "usage"
    <*> o .: "included"
    <*> o .: "rate"
    <*> o .: "wallet"
    <*> o .: "wallet_floor"
    <*> o .: "liability"
    <*> o .: "spend_cap"
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
