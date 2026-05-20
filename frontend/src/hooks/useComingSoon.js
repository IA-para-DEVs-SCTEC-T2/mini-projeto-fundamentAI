import { useState, useCallback, useRef } from 'react';

const DEFAULT_MESSAGE = 'Este recurso estará disponível em uma futura versão da plataforma.';
const DURATION_MS = 3500;

/**
 * useComingSoon — gerencia um toast temporário para features da V2.
 *
 * Uso:
 *   const { showToast, ComingSoonToast } = useComingSoon();
 *
 *   // No JSX:
 *   <button onClick={showToast}>Favoritos</button>
 *   <ComingSoonToast />
 *
 * showToast aceita uma mensagem customizada opcional:
 *   onClick={() => showToast('Alertas chegam em breve!')}
 */
export function useComingSoon(message = DEFAULT_MESSAGE) {
  const [visible, setVisible] = useState(false);
  const timerRef = useRef(null);

  const showToast = useCallback((customMessage) => {
    // Reinicia o timer se já estiver visível
    if (timerRef.current) clearTimeout(timerRef.current);
    setVisible(customMessage || message);
    timerRef.current = setTimeout(() => setVisible(false), DURATION_MS);
  }, [message]);

  const hideToast = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setVisible(false);
  }, []);

  return { showToast, hideToast, toastMessage: visible };
}

export { DEFAULT_MESSAGE as COMING_SOON_MESSAGE };
