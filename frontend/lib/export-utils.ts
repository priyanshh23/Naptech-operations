type ExportColumn<T> = {
  label: string;
  value: (row: T) => string | number | null | undefined;
};

type AnyExportColumn = {
  label: string;
  value: (row: any) => string | number | null | undefined;
};

export type ExportSection = {
  title: string;
  columns: AnyExportColumn[];
  rows: any[];
};

function escapeHtml(value: string | number | null | undefined) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function buildTableHtml<T>(title: string, columns: ExportColumn<T>[], rows: T[]) {
  return buildSectionsHtml(title, [{ title, columns, rows }]);
}

function buildSectionsHtml(title: string, sections: ExportSection[]) {
  return `
    <html>
      <head>
        <meta charset="utf-8" />
        <style>
          body { font-family: Arial, sans-serif; color: #111827; }
          h1 { font-size: 20px; margin: 0 0 6px; text-align: center; }
          h2 { font-size: 15px; margin: 18px 0 8px; color: #087B25; }
          .meta { margin: 0 0 14px; text-align: center; color: #4b5563; font-size: 12px; }
          table { border-collapse: collapse; width: 100%; font-size: 12px; }
          th, td { border: 1px solid #1f2937; padding: 7px 8px; text-align: left; vertical-align: top; }
          th { background: #f3f4f6; font-weight: 700; }
          @media print {
            body { margin: 12mm; }
            button { display: none; }
          }
        </style>
      </head>
      <body>
        <h1>${escapeHtml(title)}</h1>
        <p class="meta">Generated ${new Date().toLocaleString("en-IN")}</p>
        ${sections.map(buildSectionHtml).join("")}
      </body>
    </html>
  `;
}

function buildSectionHtml(section: ExportSection) {
  return `
    <h2>${escapeHtml(section.title)}</h2>
    <table>
      <thead>
        <tr>${section.columns.map((column) => `<th>${escapeHtml(column.label)}</th>`).join("")}</tr>
      </thead>
      <tbody>
        ${section.rows.length
          ? section.rows
              .map(
                (row) => `
                  <tr>
                    ${section.columns.map((column) => `<td>${escapeHtml(column.value(row))}</td>`).join("")}
                  </tr>
                `,
              )
              .join("")
          : `<tr><td colspan="${section.columns.length}">No rows available</td></tr>`}
      </tbody>
    </table>
  `;
}

export function downloadExcel<T>(filename: string, title: string, columns: ExportColumn<T>[], rows: T[]) {
  const html = buildTableHtml(title, columns, rows);
  const blob = new Blob([html], { type: "application/vnd.ms-excel;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename.endsWith(".xls") ? filename : `${filename}.xls`;
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function downloadExcelSections(filename: string, title: string, sections: ExportSection[]) {
  const html = buildSectionsHtml(title, sections);
  const blob = new Blob([html], { type: "application/vnd.ms-excel;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename.endsWith(".xls") ? filename : `${filename}.xls`;
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function printPdf<T>(title: string, columns: ExportColumn<T>[], rows: T[]) {
  const printWindow = window.open("", "_blank", "width=1200,height=800");
  if (!printWindow) {
    window.alert("Please allow popups to export PDF.");
    return;
  }

  printWindow.document.write(buildTableHtml(title, columns, rows));
  printWindow.document.close();
  printWindow.focus();
  printWindow.print();
}

export function printPdfSections(title: string, sections: ExportSection[]) {
  const printWindow = window.open("", "_blank", "width=1200,height=800");
  if (!printWindow) {
    window.alert("Please allow popups to export PDF.");
    return;
  }

  printWindow.document.write(buildSectionsHtml(title, sections));
  printWindow.document.close();
  printWindow.focus();
  printWindow.print();
}
