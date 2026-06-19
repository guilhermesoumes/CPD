from __future__ import annotations

from checks.templates.pdf_report import generate_pdf_report_sem_rap

def generate_study_report(**kwargs) -> None:
    generate_pdf_report_sem_rap(report_kind="Estudo", **kwargs)
