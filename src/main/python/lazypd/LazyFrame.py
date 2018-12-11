import pandas as pd
import types
import numpy as np
from inspect import signature

class LazyFrame:
  @staticmethod
  def add_lazy_columns(df:pd.DataFrame, lazy_columns:dict):
    # to satisfy the condition:
    # if name in self._info_axis:
    # in pandas.core.generic.NDFrame#__getattr__
    new_columns = np.append(df.columns, [*lazy_columns] )
    original_data = df._data.copy()
    df._data.axes[ 0 ] = pd.core.indexes.base.Index( new_columns )
    #But now we break: pandas.core.internals.BlockManager#_rebuild_blknos_and_blklocs because it counts the length of
    #self.shape[0] with lazy_columns as well. And throws AssertionError("Gaps in blk ref_locs"). To fix it we do it:
    super_copy = getattr(df,'copy')
    def copy(self,deep=True):
      data = original_data.copy(deep=deep)
      df = pd.DataFrame(data).__finalize__(self)
      return LazyFrame.add_lazy_columns(df,lazy_columns=lazy_columns)
    if super_copy != copy:
      setattr(df,'copy',types.MethodType(copy,df))

    super_getitem_array = getattr(df,'_getitem_array')
    super_get_item_cache = getattr(df,'_get_item_cache')

    def _getitem_array(self, key):
      lazy_keys = lazy_columns.keys()
      key = [k for k in key if k not in lazy_keys]
      ret_val = super_getitem_array(key)
      LazyFrame.add_lazy_columns( ret_val, lazy_columns=lazy_columns)
      return ret_val

    def _get_item_cache(self,item):
      cache = self._item_cache
      if item in lazy_columns and item not in cache:
        func = lazy_columns[ item ]
        params = [ self[param] for param in [*signature(func).parameters]]
        ret_val = func( *params )
        cache[ item ] = ret_val
        ret_val._set_as_cached(item,self)
      return super_get_item_cache(item)

    if super_get_item_cache != _get_item_cache:
      setattr(df,'_getitem_array', types.MethodType(_getitem_array,df))
      setattr(df,'_get_item_cache', types.MethodType(_get_item_cache,df))

    return df