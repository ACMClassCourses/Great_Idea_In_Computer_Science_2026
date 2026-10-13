module Main (main) where

import Test.Hspec

import qualified Homework.Week01Spec
import qualified Homework.Week02Spec
import qualified Homework.Week03Spec
import qualified Homework.Week04Spec
import qualified Homework.Week05Spec
import qualified Homework.Week06Spec
import qualified Homework.Week07Spec
import qualified Homework.Week08Spec
import qualified Homework.Week09Spec
import qualified Homework.Week10Spec
import qualified Homework.Week11Spec

main :: IO ()
main = hspec $ do
  Homework.Week01Spec.spec
  Homework.Week02Spec.spec
  Homework.Week03Spec.spec
  Homework.Week04Spec.spec
  Homework.Week05Spec.spec
  Homework.Week06Spec.spec
  Homework.Week07Spec.spec
  Homework.Week08Spec.spec
  Homework.Week09Spec.spec
  Homework.Week10Spec.spec
  Homework.Week11Spec.spec