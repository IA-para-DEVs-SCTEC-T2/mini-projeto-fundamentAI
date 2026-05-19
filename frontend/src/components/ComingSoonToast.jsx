import { Rocket, X } from 'lucide-react';

/**
 * ComingSoonToast — alerta flutuante para features da V2.
 *
 * Renderizado no nível do App para garantir posicionamento correto.
 * Controlado pelo hook useComingSoon.
 *
 * @param {string|false} message — mensagem a exibir (false = oculto)
 * @param {function}     onClose — callback para fechar manualmente
 */
export default function ComingSoonToast({ message, onClose }) {
  if (!message) return null;

  return (
    <div className="coming-soon-toast" role="status" aria-live="polite">
      <div className="coming-soon-toast-icon">
        <Rocket size={16} />
      </div>
      <span className="coming-soon-toast-text">{message}</span>
      <button
        className="coming-soon-toast-close"
        onClick={onClose}
        aria-label="Fechar aviso"
      >
        <X size={14} />
      </button>
    </div>
  );
}
