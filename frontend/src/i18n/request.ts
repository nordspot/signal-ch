import { getRequestConfig } from "next-intl/server";

export const locales = ["de", "fr", "it", "en"] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = "de";

export default getRequestConfig(async ({ locale }) => ({
  messages: (await import(`../../messages/${locale}.json`)).default,
}));
