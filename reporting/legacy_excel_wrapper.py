
from reporting.excel_exporter import export_all_results_to_excel
from reporting.compatibility_v6 import reorder_sheets

def export_legacy_excel(output_path, *args, **kwargs):
    export_all_results_to_excel(output_path, *args, **kwargs)

    try:
        import openpyxl
        wb = openpyxl.load_workbook(output_path)

        class FakeWriter:
            def __init__(self, book):
                self.book = book

        reorder_sheets(FakeWriter(wb))
        wb.save(output_path)

    except Exception:
        pass
