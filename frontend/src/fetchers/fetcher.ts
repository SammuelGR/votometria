import { API_BASE_URL } from '~/config/env';

type QueryParamValue = boolean | number | string | null | undefined;
type QueryParams = Record<string, QueryParamValue | QueryParamValue[]>;

type FetcherOptions = {
  queryParams?: QueryParams;
};

export async function fetcher<TResponse>(path: string, options?: FetcherOptions): Promise<TResponse> {
  const url = new URL(path, `${API_BASE_URL}/`);
  appendQueryParams(url, options?.queryParams);

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error('Request failed.');
  }

  return response.json() as Promise<TResponse>;
}

function appendQueryParams(url: URL, params?: QueryParams) {
  Object.entries(params ?? {}).forEach(([key, value]) => {
    const values = Array.isArray(value) ? value : [value];

    values.forEach((currentValue) => {
      if (currentValue !== null && currentValue !== undefined && currentValue !== '') {
        url.searchParams.append(key, String(currentValue));
      }
    });
  });
}
