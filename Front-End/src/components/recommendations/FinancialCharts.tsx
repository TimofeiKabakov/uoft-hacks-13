/**
 * Financial Charts Component
 * 
 * Animated charts showing cash flow, spending by category, and stability trends.
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { GlassCard } from '@/components/ui/GlassCard';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { fadeInUp, staggerContainer } from '@/lib/animations';
import type { FinancialSnapshot, TimeRange, AccountScope } from '@/types/recommendations';

interface FinancialChartsProps {
  snapshot: FinancialSnapshot;
}

export function FinancialCharts({ snapshot }: FinancialChartsProps) {
  const [timeRange, setTimeRange] = useState<TimeRange>(30);
  const [accountScope, setAccountScope] = useState<AccountScope>('single');
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  const timeRanges: TimeRange[] = [30, 60, 90];
  
  // Filter data based on time range (simplified for demo)
  const filteredCashFlow = snapshot.cashFlow.slice(-Math.ceil(timeRange / 10));
  
  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="show"
      className="space-y-6"
    >
      {/* Controls */}
      <motion.div variants={fadeInUp} className="flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Time Range:</span>
          <div className="flex gap-1">
            {timeRanges.map((range) => (
              <Button
                key={range}
                variant={timeRange === range ? 'default' : 'outline'}
                size="sm"
                onClick={() => setTimeRange(range)}
              >
                {range}d
              </Button>
            ))}
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Scope:</span>
          <div className="flex gap-1">
            <Button
              variant={accountScope === 'single' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setAccountScope('single')}
            >
              Single Account
            </Button>
            <Button
              variant={accountScope === 'portfolio' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setAccountScope('portfolio')}
            >
              Portfolio
            </Button>
          </div>
        </div>
      </motion.div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cash Flow Chart */}
        <motion.div variants={fadeInUp}>
          <GlassCard className="p-5">
            <h3 className="font-semibold text-foreground mb-4">Inflow vs Outflow</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={filteredCashFlow}>
                  <defs>
                    <linearGradient id="inflowGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(var(--success))" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="hsl(var(--success))" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="outflowGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(var(--destructive))" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="hsl(var(--destructive))" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 12 }}
                    className="text-muted-foreground"
                  />
                  <YAxis 
                    tick={{ fontSize: 12 }}
                    tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
                    className="text-muted-foreground"
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                    formatter={(value: number) => [`$${value.toLocaleString()}`, '']}
                  />
                  <Area
                    type="monotone"
                    dataKey="inflow"
                    stroke="hsl(var(--success))"
                    fill="url(#inflowGradient)"
                    strokeWidth={2}
                    name="Inflow"
                  />
                  <Area
                    type="monotone"
                    dataKey="outflow"
                    stroke="hsl(var(--destructive))"
                    fill="url(#outflowGradient)"
                    strokeWidth={2}
                    name="Outflow"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>
        </motion.div>

        {/* Spending by Category */}
        <motion.div variants={fadeInUp}>
          <GlassCard className="p-5">
            <h3 className="font-semibold text-foreground mb-4">Spending by Category</h3>
            <div className="h-64 flex items-center">
              <div className="w-1/2 h-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={snapshot.spendingByCategory}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={80}
                      paddingAngle={2}
                      onMouseEnter={(_, index) => setActiveCategory(snapshot.spendingByCategory[index].name)}
                      onMouseLeave={() => setActiveCategory(null)}
                    >
                      {snapshot.spendingByCategory.map((entry, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={entry.color}
                          opacity={activeCategory === null || activeCategory === entry.name ? 1 : 0.3}
                          style={{ cursor: 'pointer' }}
                        />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                      }}
                      formatter={(value: number) => [`$${value.toLocaleString()}`, '']}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="w-1/2 space-y-2">
                {snapshot.spendingByCategory.map((category) => (
                  <div
                    key={category.name}
                    className={`flex items-center justify-between p-2 rounded-lg transition-colors cursor-pointer ${
                      activeCategory === category.name ? 'bg-muted' : ''
                    }`}
                    onMouseEnter={() => setActiveCategory(category.name)}
                    onMouseLeave={() => setActiveCategory(null)}
                  >
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: category.color }}
                      />
                      <span className="text-sm text-foreground">{category.name}</span>
                    </div>
                    <span className="text-sm font-medium text-foreground">
                      ${category.value.toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </GlassCard>
        </motion.div>

        {/* Stability Trend */}
        <motion.div variants={fadeInUp} className="lg:col-span-2">
          <GlassCard className="p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-foreground">Stability Trend</h3>
              <Badge variant="secondary" className="text-xs">
                6-week rolling average
              </Badge>
            </div>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={snapshot.stabilityTrend}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 12 }}
                    className="text-muted-foreground"
                  />
                  <YAxis 
                    domain={[50, 100]}
                    tick={{ fontSize: 12 }}
                    className="text-muted-foreground"
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="score"
                    stroke="hsl(var(--primary))"
                    strokeWidth={3}
                    dot={{ fill: 'hsl(var(--primary))', strokeWidth: 0, r: 4 }}
                    activeDot={{ r: 6, fill: 'hsl(var(--primary))' }}
                    name="Stability Score"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>
        </motion.div>
      </div>
    </motion.div>
  );
}
