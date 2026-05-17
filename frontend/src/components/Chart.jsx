import { DollarSign } from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts';

export default function Chart({ priceHistory }) {
  if (!priceHistory || priceHistory.length === 0) return null;

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title"><DollarSign size={18} /> Histórico de Preços (5 Anos)</h3>
      </div>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={priceHistory} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="gradTeal" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#00e6d2" stopOpacity={0.28} />
                <stop offset="95%" stopColor="#00e6d2" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.07)" vertical={false} />
            <XAxis
              dataKey="date"
              stroke="rgba(255,255,255,0.3)"
              tick={{ fill: 'rgba(255,255,255,0.45)', fontSize: 11 }}
              tickFormatter={(v) => new Date(v).getFullYear()}
              minTickGap={40}
            />
            <YAxis
              stroke="rgba(255,255,255,0.3)"
              tick={{ fill: 'rgba(255,255,255,0.45)', fontSize: 11 }}
              domain={['auto', 'auto']}
              tickFormatter={(v) => `R$${v}`}
              width={60}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#161a22', borderColor: 'rgba(255,255,255,0.1)', borderRadius: 8 }}
              itemStyle={{ color: '#00e6d2' }}
              labelStyle={{ color: '#8b949e', marginBottom: 4 }}
              formatter={(v) => [`R$ ${Number(v).toFixed(2)}`, 'Preço']}
            />
            <Area
              type="monotone"
              dataKey="close"
              stroke="#00e6d2"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#gradTeal)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
