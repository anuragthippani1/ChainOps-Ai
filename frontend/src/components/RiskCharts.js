import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const RiskCharts = ({ politicalRisks, scheduleRisks }) => {
  // Prepare data for political risk by country
  const politicalRiskData = politicalRisks.reduce((acc, risk) => {
    const existing = acc.find(item => item.country === risk.country);
    if (existing) {
      existing.riskLevel = Math.max(existing.riskLevel, risk.likelihood_score);
      existing.count += 1;
    } else {
      acc.push({
        country: risk.country,
        riskLevel: risk.likelihood_score,
        count: 1
      });
    }
    return acc;
  }, []);

  // Prepare data for schedule risk by country
  const scheduleRiskData = scheduleRisks.reduce((acc, risk) => {
    const existing = acc.find(item => item.country === risk.country);
    if (existing) {
      existing.avgDelay = (existing.avgDelay * existing.count + risk.delay_days) / (existing.count + 1);
      existing.count += 1;
    } else {
      acc.push({
        country: risk.country,
        avgDelay: risk.delay_days,
        count: 1
      });
    }
    return acc;
  }, []);

  // Risk level distribution
  const riskLevelDistribution = [
    { name: 'Low (1-2)', value: politicalRisks.filter(r => r.likelihood_score <= 2).length, color: '#10B981' },
    { name: 'Medium (3)', value: politicalRisks.filter(r => r.likelihood_score === 3).length, color: '#F59E0B' },
    { name: 'High (4-5)', value: politicalRisks.filter(r => r.likelihood_score >= 4).length, color: '#EF4444' }
  ];

  // Schedule delay distribution
  const delayDistribution = [
    { name: 'On Time', value: scheduleRisks.filter(r => r.delay_days === 0).length, color: '#10B981' },
    { name: '1-7 Days', value: scheduleRisks.filter(r => r.delay_days > 0 && r.delay_days <= 7).length, color: '#F59E0B' },
    { name: '8-30 Days', value: scheduleRisks.filter(r => r.delay_days > 7 && r.delay_days <= 30).length, color: '#EF4444' },
    { name: '30+ Days', value: scheduleRisks.filter(r => r.delay_days > 30).length, color: '#7C2D12' }
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Political Risk by Country */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Political Risk by Country</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={politicalRiskData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="country" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="riskLevel" fill="#EF4444" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Schedule Delays by Country */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Average Delay by Country</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={scheduleRiskData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="country" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="avgDelay" fill="#F59E0B" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Risk Level Distribution */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Political Risk Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={riskLevelDistribution}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value }) => `${name}: ${value}`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {riskLevelDistribution.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Delay Distribution */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Schedule Delay Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={delayDistribution}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value }) => `${name}: ${value}`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {delayDistribution.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default RiskCharts;
