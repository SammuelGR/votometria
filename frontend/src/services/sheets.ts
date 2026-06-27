import Papa from 'papaparse';

const SHEET_ID = import.meta.env.VITE_GOOGLE_SHEETS_ID as string | undefined;

/**
 * Builds the public CSV export URL for a given tab of the configured spreadsheet.
 * Uses the Google Visualization endpoint, which returns CSV when the sheet is
 * published or shared by link. No credentials are needed on the client.
 */
export function sheetCsvUrl(tabName: string): string {
  if (!SHEET_ID) {
    throw new Error('VITE_GOOGLE_SHEETS_ID não está configurado. Defina o ID da planilha no arquivo .env do frontend.');
  }

  const params = new URLSearchParams({ tqx: 'out:csv', sheet: tabName });

  return `https://docs.google.com/spreadsheets/d/${SHEET_ID}/gviz/tq?${params.toString()}`;
}

/** Fetches the raw CSV text of a spreadsheet tab. */
export async function fetchSheetCsv(tabName: string): Promise<string> {
  const response = await fetch(sheetCsvUrl(tabName));

  if (!response.ok) {
    throw new Error(`Falha ao buscar a aba '${tabName}': ${response.status} ${response.statusText}`);
  }

  return response.text();
}

/** Parses CSV text into typed rows using the header row as keys. */
export function parseCsv<T>(csv: string): T[] {
  const result = Papa.parse<T>(csv, {
    header: true,
    skipEmptyLines: true,
    transformHeader: (header) => header.trim(),
  });

  return result.data;
}
