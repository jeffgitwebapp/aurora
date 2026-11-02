/**
 * Conversão de localização feita somente neste aparelho: as coordenadas do
 * navegador são comparadas com as capitais abaixo e descartadas. Apenas a
 * cidade/UF confirmada pela usuária é enviada ao backend.
 */

export interface CityState {
  city: string;
  state: string;
}

const CAPITALS: Array<CityState & { lat: number; lon: number }> = [
  { city: "Rio Branco", state: "AC", lat: -9.97, lon: -67.81 },
  { city: "Maceió", state: "AL", lat: -9.67, lon: -35.74 },
  { city: "Macapá", state: "AP", lat: 0.03, lon: -51.07 },
  { city: "Manaus", state: "AM", lat: -3.12, lon: -60.02 },
  { city: "Salvador", state: "BA", lat: -12.97, lon: -38.5 },
  { city: "Fortaleza", state: "CE", lat: -3.73, lon: -38.53 },
  { city: "Brasília", state: "DF", lat: -15.79, lon: -47.88 },
  { city: "Vitória", state: "ES", lat: -20.32, lon: -40.34 },
  { city: "Goiânia", state: "GO", lat: -16.69, lon: -49.26 },
  { city: "São Luís", state: "MA", lat: -2.53, lon: -44.3 },
  { city: "Cuiabá", state: "MT", lat: -15.6, lon: -56.1 },
  { city: "Campo Grande", state: "MS", lat: -20.46, lon: -54.62 },
  { city: "Belo Horizonte", state: "MG", lat: -19.92, lon: -43.94 },
  { city: "Belém", state: "PA", lat: -1.46, lon: -48.5 },
  { city: "João Pessoa", state: "PB", lat: -7.12, lon: -34.86 },
  { city: "Curitiba", state: "PR", lat: -25.43, lon: -49.27 },
  { city: "Recife", state: "PE", lat: -8.05, lon: -34.88 },
  { city: "Teresina", state: "PI", lat: -5.09, lon: -42.8 },
  { city: "Rio de Janeiro", state: "RJ", lat: -22.91, lon: -43.17 },
  { city: "Natal", state: "RN", lat: -5.79, lon: -35.21 },
  { city: "Porto Alegre", state: "RS", lat: -30.03, lon: -51.23 },
  { city: "Porto Velho", state: "RO", lat: -8.76, lon: -63.9 },
  { city: "Boa Vista", state: "RR", lat: 2.82, lon: -60.67 },
  { city: "Florianópolis", state: "SC", lat: -27.59, lon: -48.55 },
  { city: "São Paulo", state: "SP", lat: -23.55, lon: -46.63 },
  { city: "Aracaju", state: "SE", lat: -10.91, lon: -37.07 },
  { city: "Palmas", state: "TO", lat: -10.18, lon: -48.33 },
];

const MAX_DISTANCE_KM = 40;

function distanceKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const toRad = (degrees: number) => (degrees * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  return 6371 * 2 * Math.asin(Math.sqrt(a));
}

/** Capital mais próxima dentro de 40 km, ou null quando não há correspondência. */
export function nearestCapital(lat: number, lon: number): CityState | null {
  let best: { capital: CityState; distance: number } | null = null;
  for (const capital of CAPITALS) {
    const distance = distanceKm(lat, lon, capital.lat, capital.lon);
    if (!best || distance < best.distance) {
      best = { capital: { city: capital.city, state: capital.state }, distance };
    }
  }
  return best && best.distance <= MAX_DISTANCE_KM ? best.capital : null;
}

/** Interpreta “Cidade / UF” (também aceita “-” ou “,” como separador). */
export function parseCityState(text: string): CityState | null {
  const match = text.trim().match(/^(.+?)\s*[/,-]\s*([A-Za-z]{2})$/);
  if (!match) {
    return null;
  }
  const city = match[1].replace(/\s+/g, " ").trim();
  return city ? { city, state: match[2].toUpperCase() } : null;
}

export function formatCityState({ city, state }: CityState): string {
  return `${city} / ${state}`;
}
