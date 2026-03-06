"""Accumulate validation results and emit reports via logging."""

from __future__ import annotations

from typing import Any

from meta.logger import get_app_logger

from .model import (
    FileValidationMessages,
    ValidationError,
    ValidationReport,
    ValidationStatistics,
    ValidationWarning,
)


class Reporter:
    """Collects validation errors and warnings and emits a report."""

    def __init__(
        self,
        contributors: dict[str, Any],
        teams: dict[str, Any],
    ) -> None:
        """Initialize file buckets for contributors and teams."""
        self._contributors_count = len(contributors)
        self._teams_count = len(teams)
        self._files: dict[str, FileValidationMessages] = {
            file_path: FileValidationMessages() for file_path in contributors
        }

        self.logger = get_app_logger()

        for file_path in teams:
            self._files[file_path] = FileValidationMessages()

    def insert_error(self, error: ValidationError) -> None:
        """Insert a validation error into the per-file bucket."""
        if error.file not in self._files:
            self._files[error.file] = FileValidationMessages()
        self._files[error.file].errors.append(error)

    def insert_errors(self, errors: list[ValidationError]) -> None:
        """Insert multiple validation errors."""
        for error in errors:
            self.insert_error(error)

    def insert_warning(self, warning: ValidationWarning) -> None:
        """Insert a validation warning into the per-file bucket."""
        if warning.file not in self._files:
            self._files[warning.file] = FileValidationMessages()
        self._files[warning.file].warnings.append(warning)

    def insert_warnings(self, warnings: list[ValidationWarning]) -> None:
        """Insert multiple validation warnings."""
        for warning in warnings:
            self.insert_warning(warning)

    def build_report(self) -> ValidationReport:
        """Compute stats and return a ValidationReport."""
        total_errors = sum(len(m.errors) for m in self._files.values())
        total_warnings = sum(len(m.warnings) for m in self._files.values())
        valid_files = sum(1 for m in self._files.values() if not m.errors)
        invalid_files = len(self._files) - valid_files
        stats = ValidationStatistics(
            contributors_count=self._contributors_count,
            teams_count=self._teams_count,
            valid_files_count=valid_files,
            invalid_files_count=invalid_files,
            total_errors=total_errors,
            total_warnings=total_warnings,
        )
        return ValidationReport(
            valid=(invalid_files == 0),
            stats=stats,
            files=self._files,
        )

    def emit(self) -> ValidationReport:
        """Log the report and return it."""
        report = self.build_report()
        self.logger.info("===== SUMMARY =====")
        self.logger.info("Contributors: %s", report.stats.contributors_count)
        self.logger.info("Teams: %s", report.stats.teams_count)
        self.logger.info("Valid files: %s", report.stats.valid_files_count)
        self.logger.info("Invalid files: %s", report.stats.invalid_files_count)
        self.logger.info("Total errors: %s", report.stats.total_errors)
        self.logger.info("Total warnings: %s", report.stats.total_warnings)

        if report.stats.total_errors > 0:
            self.logger.error("===== ERRORS =====")
            for file_path, messages in report.files.items():
                if not messages.errors:
                    continue
                self.logger.error("%s", file_path)
                for err in messages.errors:
                    self.logger.error("  - %s", err.message)

        if report.stats.total_warnings > 0:
            self.logger.warning("===== WARNINGS =====")
            for file_path, messages in report.files.items():
                if not messages.warnings:
                    continue
                self.logger.warning("%s", file_path)
                for warn in messages.warnings:
                    self.logger.warning("  - %s", warn.message)

        if not report.valid:
            self.logger.error(
                "Validation failed with %s error(s) in %s file(s)",
                report.stats.total_errors,
                report.stats.invalid_files_count,
            )
        else:
            self.logger.success("Validation passed!")
        return report
