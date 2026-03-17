from tkinter import filedialog, messagebox
import os
import logging
from utils.logger import setup_logger
from utils.pdf_report import create_pdf_report, open_pdf_report

logger = setup_logger(__name__)


def export_report(self):
    """Export a PDF report for the last analysis."""
    logger.info("Demande d'export PDF")
    if not self.last_results_data or not self.image_path:
        logger.warning("Pas de données disponibles pour l'export PDF")
        msg = (
            self.i18n.t("analysis_error")
            if hasattr(self, "i18n")
            else "Pas de résultat à exporter"
        )
        self.update_status(msg)
        messagebox.showinfo(
            self.i18n.t("pdf") if hasattr(self, "i18n") else "Exporter en PDF",
            (
                self.i18n.t("analysis_error")
                if hasattr(self, "i18n")
                else "Aucun résultat disponible pour exporter. Analysez d'abord une image."
            ),
        )
        return

    suggested_name = self.computed_insect_name or "rapport"
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")],
        initialdir=os.path.expanduser("~/Documents"),
        initialfile=f"{suggested_name}.pdf",
        title=self.i18n.t("pdf") if hasattr(self, "i18n") else "Exporter en PDF",
    )
    if not file_path:
        logger.info("Export PDF annulé par l'utilisateur")
        return

    try:
        logger.info(f"Création du rapport PDF: {file_path}")
        create_pdf_report(
            output_path=file_path,
            image_path=self.image_path,
            species_name=self.computed_insect_name,
            results_data=self.last_results_data,
            avg_conf=self.last_avg_conf,
            reliable=self.last_reliable,
            gbif_url=self.last_gbif_url,
            wikipedia_summary=self.last_wikipedia_summary,
        )
        logger.info("Rapport PDF créé avec succès")
        self.update_status(
            f"{self.i18n.t('pdf') if hasattr(self, 'i18n') else 'Rapport exporté'} : {os.path.basename(file_path)}"
        )
        messagebox.showinfo(
            self.i18n.t("pdf") if hasattr(self, "i18n") else "Exporter en PDF",
            (
                self.i18n.t("ready")
                if hasattr(self, "i18n")
                else f"Rapport généré avec succès:\n{file_path}"
            ),
        )
        open_pdf_report(file_path)
    except Exception as e:
        logger.error(f"Erreur lors de l'export PDF: {e}", exc_info=True)
        self.update_status(
            self.i18n.t("analysis_error")
            if hasattr(self, "i18n")
            else "Échec de l'export PDF"
        )
        messagebox.showerror(
            self.i18n.t("pdf") if hasattr(self, "i18n") else "Exporter en PDF",
            (
                self.i18n.t("analysis_error")
                if hasattr(self, "i18n")
                else f"Impossible d'exporter le rapport:\n{e}"
            ),
        )
