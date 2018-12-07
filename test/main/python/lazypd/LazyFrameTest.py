from lazypd.LazyFrame import LazyFrame
import unittest
import pandas as pd
import inspect
import os
import math

class LazyFrameTest(unittest.TestCase):

  def get_file_next_to_me(self,file_name):
    class_file_name = inspect.getfile(self.__class__)
    file = os.path.join(os.path.dirname( class_file_name ), file_name)
    return file

  def _df(self):
    df = pd.read_csv(self.get_file_next_to_me('test_data.csv'))
    LazyFrame.add_lazy_columns(df, lazy_columns= {
      'Square' : lambda X, Y: X*Y,
      'Perimeter': lambda X, Y: 2*math.pi * (X+Y)
    })
    return df

  def testExplicitAccess(self):
    df = self._df()
    x = df.Square
    self.assertEqual(35,x.sum())

  def testAccessByName(self):
    df = self._df()
    x = df['Square']
    self.assertEqual(35,x.sum())

  def testAccessByName2(self):
    df = self._df()
    x = df[['X','Y','Square']]
    # self.assertEqual(35,x.sum()['Square'])

  def testGroupBy(self):
    df = self._df()
    x = df.groupby(['name'])
    x = x.sum().reset_index()
    self.assertEqual(35,x)
