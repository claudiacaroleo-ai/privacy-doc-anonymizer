import csv
import json
import tempfile
import unittest
from pathlib import Path

import core


class CoreRedactionTests(unittest.TestCase):
    def test_partial_overlap_is_merged_without_corrupting_text(self):
        spans = [
            core.Span("a.txt", "private_person", "cdefg", 2, 7, None, True, "PERSON_1"),
            core.Span("a.txt", "private_person", "fghi", 5, 9, None, True, "PERSON_2"),
        ]

        self.assertEqual(core.preview_redacted_text("abcdefghij", spans), "ab[PERSON_1]j")

    def test_mapping_uses_only_redacted_spans_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            input_file = base / "input.txt"
            output_dir = base / "out"
            input_file.write_text("Mario Rossi incontra Luca Bianchi", encoding="utf-8")

            spans = [
                core.Span("input.txt", "private_person", "Mario Rossi", 0, 11, 0.95, True),
                core.Span("input.txt", "private_person", "Luca Bianchi", 21, 33, 0.95, False),
            ]

            errors = core.save_outputs([str(input_file)], spans, str(output_dir))

            self.assertEqual(errors, [])
            reserved_dir = output_dir / core.RESERVED_OUTPUT_SUBDIR
            safe_dir = output_dir / core.SAFE_OUTPUT_SUBDIR

            self.assertTrue((safe_dir / "input_txt_anonymized.txt").exists())
            self.assertFalse((output_dir / "input_txt_anonymized.txt").exists())

            mapping = json.loads((reserved_dir / "mapping_entities.json").read_text(encoding="utf-8"))
            self.assertEqual(len(mapping), 1)
            self.assertEqual(mapping[0]["text"], "Mario Rossi")

            with (reserved_dir / "index_occurrences.csv").open(encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["text"], "Mario Rossi")

    def test_entity_normalization_reuses_code(self):
        spans = [
            core.Span("a.txt", "private_email", "INFO@EXAMPLE.COM", 0, 16, None, True),
            core.Span("b.txt", "private_email", "info@example.com", 0, 16, None, True),
        ]

        registry = core.build_entity_registry(spans)

        self.assertEqual(len(registry), 1)
        self.assertEqual(spans[0].code, spans[1].code)

    def test_output_name_keeps_extension_to_avoid_collision(self):
        self.assertTrue(core._output_path_for("contract.pdf", "out").endswith("contract_pdf_anonymized.txt"))
        self.assertTrue(core._output_path_for("contract.docx", "out").endswith("contract_docx_anonymized.txt"))

    def test_regex_validators_for_italian_identifiers(self):
        self.assertTrue(core._valid_piva("01114601006"))
        self.assertFalse(core._valid_piva("01114601007"))
        self.assertTrue(core._valid_iban("IT60X0542811101000000123456"))
        self.assertFalse(core._valid_iban("IT61X0542811101000000123456"))

    def test_piva_regex_does_not_also_become_phone(self):
        spans = core._detect_regex_spans(
            "P.IVA 01114601006",
            "a.txt",
            {"private_id", "private_phone"},
            set(),
        )

        self.assertEqual(len(spans), 1)
        self.assertEqual(spans[0].label, "private_id")

    def test_xlsx_is_extracted_as_compact_text(self):
        try:
            import openpyxl
        except ImportError:
            self.skipTest("openpyxl non installato")

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "clienti.xlsx"
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Clienti"
            ws.append(["Nome", "Email"])
            ws.append(["Mario Rossi", "mario.rossi@example.com"])
            wb.save(path)

            text = core.extract_text(str(path))

            self.assertIn("[Sheet: Clienti]", text)
            self.assertIn("Nome | Email", text)
            self.assertIn("Row 2: Nome: Mario Rossi | Email: mario.rossi@example.com", text)

    def test_supplier_field_is_detected_automatically(self):
        spans = core._detect_context_spans(
            "Fornitore: ACME Srl | P.IVA: 01114601006",
            "a.txt",
            {"private_organization"},
            set(),
        )

        self.assertEqual(len(spans), 1)
        self.assertEqual(spans[0].label, "private_organization")
        self.assertEqual(spans[0].text, "ACME Srl")
        self.assertTrue(spans[0].will_redact)

    def test_collect_unsupported_files_reports_ignored_extensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "ok.xlsx").write_text("not really xlsx, but extension is supported", encoding="utf-8")
            (base / "ok.txt").write_text("hello", encoding="utf-8")
            (base / "foto.jpg").write_text("image", encoding="utf-8")
            (base / "note.rtf").write_text("rtf", encoding="utf-8")

            supported = [Path(path).name for path in core.collect_files(str(base))]
            unsupported = [Path(path).name for path in core.collect_unsupported_files(str(base))]

            self.assertEqual(supported, ["ok.txt", "ok.xlsx"])
            self.assertEqual(unsupported, ["foto.jpg", "note.rtf"])


if __name__ == "__main__":
    unittest.main()
