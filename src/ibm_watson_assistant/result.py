# from kbc.result import ResultWriter, KBCTableDef
#
#
# class LineItemWriter(ResultWriter):
#     def __init__(self, result_dir_path, extraction_time, additional_pk: list = None, prefix='', file_headers=None):
#         pk = ['id']
#         if additional_pk:
#             pk.extend(additional_pk)
#         file_name = f'{prefix}line_item'
#         ResultWriter.__init__(self, result_dir_path,
#                               KBCTableDef(name=file_name, pk=pk, columns=file_headers.get(f'{file_name}.csv', []),
#                                           destination=''),
#                               fix_headers=True, flatten_objects=True, child_separator='__')
