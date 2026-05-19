import { useEffect } from 'react';

const APP_NAME = 'FundamentAI';

/**
 * Atualiza o document.title com o padrão "[Página] | FundamentAI".
 * Quando pageTitle é nulo/undefined, usa apenas "FundamentAI".
 *
 * @param {string|null} pageTitle - Nome da página atual
 */
export function usePageTitle(pageTitle) {
  useEffect(() => {
    document.title = pageTitle ? `${pageTitle} | ${APP_NAME}` : APP_NAME;
  }, [pageTitle]);
}
