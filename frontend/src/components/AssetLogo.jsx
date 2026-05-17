/**
 * AssetLogo — exibe o logo da empresa/FII.
 * Tenta carregar via logo.clearbit.com; se falhar, mostra fallback com iniciais.
 */

// Mapeamento ticker → domínio para logos via Clearbit
const TICKER_DOMAIN = {
  // Ações
  PETR4: 'petrobras.com.br', PETR3: 'petrobras.com.br',
  VALE3: 'vale.com',
  ITUB4: 'itau.com.br',      ITUB3: 'itau.com.br',
  BBAS3: 'bb.com.br',
  BBDC4: 'bradesco.com.br',  BBDC3: 'bradesco.com.br',
  SANB11:'santander.com.br',
  WEGE3: 'weg.net',
  EMBR3: 'embraer.com',
  RENT3: 'localiza.com',
  MGLU3: 'magazineluiza.com.br',
  LREN3: 'lojasrenner.com.br',
  ABEV3: 'ambev.com.br',
  SUZB3: 'suzano.com.br',
  RADL3: 'raiadrogasil.com.br',
  HAPV3: 'hapvida.com.br',
  RDOR3: 'rededorsirio.com.br',
  EGIE3: 'engie.com.br',
  TAEE11:'taesa.com.br',
  CMIG4: 'cemig.com.br',
  ELET3: 'eletrobras.com',
  EQTL3: 'equatorialenergia.com.br',
  VIVT3: 'vivo.com.br',
  TIMS3: 'tim.com.br',
  RAIL3: 'rumolog.com',
  CCRO3: 'grupoccr.com.br',
  PRIO3: 'petrorio.com.br',
  CSAN3: 'cosan.com',
  // FIIs — sem domínio próprio, usam emoji/ícone
};

// Emojis fallback por segmento/setor
const SECTOR_EMOJI = {
  'Petróleo': '🛢️', 'Mineração': '⛏️', 'Bancos': '🏦',
  'Indústria': '⚙️', 'Serviços': '🔧', 'Varejo': '🛒',
  'Bebidas': '🍺', 'Papel e Celulose': '📄', 'Saúde': '🏥',
  'Energia': '⚡', 'Telecom': '📡', 'Logística': '🚚',
  'Aeronáutica': '✈️',
  // FII segments
  'Shopping': '🛍️', 'Escritórios': '🏢', 'Papel': '📋',
  'Fundo de Fundos': '📦', 'Renda Urbana': '🏪',
  'Fundos Imobiliários': '🏗️',
};

import { useState } from 'react';

export default function AssetLogo({ ticker, sector, size = 36 }) {
  const [imgError, setImgError] = useState(false);
  const domain = TICKER_DOMAIN[ticker];
  const emoji  = SECTOR_EMOJI[sector] || '📊';

  // Iniciais para fallback visual
  const initials = (ticker || '').slice(0, 2).toUpperCase();

  const style = {
    width: size,
    height: size,
    borderRadius: size * 0.22,
    flexShrink: 0,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
    background: 'rgba(255,255,255,0.06)',
    border: '1px solid rgba(255,255,255,0.1)',
    fontSize: size * 0.45,
  };

  if (domain && !imgError) {
    return (
      <div style={style}>
        <img
          src={`https://logo.clearbit.com/${domain}`}
          alt={ticker}
          width={size}
          height={size}
          style={{ objectFit: 'contain', borderRadius: size * 0.2 }}
          onError={() => setImgError(true)}
        />
      </div>
    );
  }

  // Fallback: emoji do setor ou iniciais
  return (
    <div style={style}>
      {emoji !== '📊' ? (
        <span style={{ lineHeight: 1 }}>{emoji}</span>
      ) : (
        <span style={{
          fontFamily: 'var(--font-display)',
          fontWeight: 800,
          fontSize: size * 0.32,
          color: 'var(--primary)',
          lineHeight: 1,
        }}>
          {initials}
        </span>
      )}
    </div>
  );
}
