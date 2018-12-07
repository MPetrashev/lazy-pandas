import pandas as pd
import types
import numpy as np

class LazyFrame:
  @staticmethod
  def add_lazy_columns(df:pd.DataFrame, lazy_columns:dict):
    # to satisfy the condition:
    # if name in self._info_axis:
    # in pandas.core.generic.NDFrame#__getattr__
    new_columns = np.append(df.columns, [*lazy_columns] )
    df._data.axes[ 0 ] = pd.core.indexes.base.Index( new_columns )

    super_getitem_array = getattr(df,'_getitem_array')
    super_get_item_cache = getattr(df,'_get_item_cache')

    def _getitem_array(self, key):
      key.remove('Square')
      ret_val = super_getitem_array(key)
      LazyFrame.add_lazy_columns( ret_val, lazy_columns=lazy_columns)
      return ret_val

    def _get_item_cache(self,item):
      cache = self._item_cache
      if item in lazy_columns and item not in cache:
        ret_val = self.X * self.Y
        cache[ item ] = ret_val
        ret_val._set_as_cached(item,self)
      return super_get_item_cache(item)

    if super_get_item_cache != _get_item_cache:
      setattr(df,'_getitem_array', types.MethodType(_getitem_array,df))
      setattr(df,'_get_item_cache', types.MethodType(_get_item_cache,df))