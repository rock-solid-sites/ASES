{-# LANGUAGE BangPatterns #-}
-- P5 synthetic crash-recovery research only. SIGKILL != power failure.
import Control.Monad (foldM, unless, when)
import Data.Char (isAscii, isAlphaNum)
import Data.List (nub)
import System.Directory (doesFileExist)
import System.Environment (getArgs)
import System.Exit (die)
import System.IO (hFlush, stdout)
import System.Posix.IO (openFd, closeFd, fdWrite, defaultFileFlags, OpenMode(WriteOnly), OpenFileFlags(append))
import System.Posix.Unistd (fileSynchronise)
import Text.Read (readMaybe)

data Ledger = Ledger { reserved :: !Integer, charged :: !Integer, entries :: !Int, ids :: ![String] }
empty :: Ledger
empty = Ledger 0 0 0 []

splitRecord :: String -> Either String (String, Integer, Integer)
splitRecord s = case break (=='|') s of
  (ident, '|':rest) -> case break (=='|') rest of
    (units, '|':amount) | not (null ident) && length ident <= 12
      && all (\c -> isAscii c && isAlphaNum c) ident ->
        case (readMaybe units :: Maybe Integer, readMaybe amount :: Maybe Integer) of
          (Just u, Just v) | u > 0 && v >= 0 -> Right (ident,u,v)
          _ -> Left "bad amounts in journal"
    _ -> Left "malformed journal line"
  _ -> Left "malformed journal line"

replay :: FilePath -> IO Ledger
replay path = do
  exists <- doesFileExist path
  content <- if exists then readFile path else pure ""
  case foldM step empty (lines content) of
    Left err -> die err
    Right st -> pure st
  where
    step st line = do
      (ident,u,v) <- splitRecord line
      let !next = Ledger (reserved st+u) (charged st+v) (entries st+1) (ident:ids st)
      Right next

emit :: String -> IO ()
emit value = putStrLn value >> hFlush stdout

gate :: IO ()
gate = do
  line <- getLine
  unless (line == "GO") (die "checkpoint release denied")

writeAll fd s | null s = pure ()
writeAll fd s = do
  n <- fdWrite fd s
  when (n <= 0) (die "journal write did not advance")
  writeAll fd (drop (fromIntegral n) s)

appendRecord :: FilePath -> String -> Integer -> Integer -> IO ()
appendRecord path ident u v = do
  fd <- openFd path WriteOnly (Just 0o600) defaultFileFlags { append = True }
  writeAll fd (ident ++ "|" ++ show u ++ "|" ++ show v ++ "\n")
  fileSynchronise fd
  closeFd fd

applyRequest :: FilePath -> String -> String -> String -> Integer -> Integer -> Integer -> Integer -> Bool -> IO ()
applyRequest path mode hook ident units amount capacity spendCap paid = do
  unless (mode `elem` ["correct","duplicate","early_ack"]
    && hook `elem` ["none","before","after_sync","after_ack"]
    && not (null ident) && length ident <= 12
    && all (\c -> isAscii c && isAlphaNum c) ident) (die "invalid mode/hook/id")
  st <- replay path
  if mode /= "duplicate" && ident `elem` ids st
    then emit "DUPLICATE"
    else if units <= 0 || amount < 0 || capacity < 0 || spendCap < 0
      || (amount > 0 && not paid)
      || reserved st + units > capacity || charged st + amount > spendCap
      then emit "DENY"
      else do
        when (hook == "before") (emit "PREPARED" >> gate)
        when (mode == "early_ack") $ do
          emit "ACK"
          when (hook == "after_ack") gate
        appendRecord path ident units amount
        when (hook == "after_sync") (emit "DURABLE" >> gate)
        when (mode /= "early_ack") $ do
          emit "ACK"
          when (hook == "after_ack") gate

main :: IO ()
main = do
  args <- getArgs
  case args of
    ["inspect",path] -> do
      st <- replay path
      emit ("STATE|" ++ show (reserved st) ++ "|" ++ show (charged st)
        ++ "|" ++ show (entries st) ++ "|" ++ show (length (nub (ids st))))
    ["apply",path,mode,hook,ident,u,c,cap,spend,opt] ->
      case (readMaybe u :: Maybe Integer, readMaybe c :: Maybe Integer,
            readMaybe cap :: Maybe Integer, readMaybe spend :: Maybe Integer,
            opt) of
        (Just units,Just amount,Just capacity,Just spendCap,"true") ->
          applyRequest path mode hook ident units amount capacity spendCap True
        (Just units,Just amount,Just capacity,Just spendCap,"false") ->
          applyRequest path mode hook ident units amount capacity spendCap False
        _ -> die "invalid numeric or authorization arguments"
    _ -> die "usage: inspect JOURNAL | apply JOURNAL MODE HOOK ID UNITS CHARGE CAPACITY SPEND_CAP OPT_IN"
