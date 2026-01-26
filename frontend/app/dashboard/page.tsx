'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import { Nav } from '@/components/Nav';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

export default function Dashboard() {
    const [metrics, setMetrics] = useState<any[]>([]);
    const [risks, setRisks] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [mRes, rRes] = await Promise.all([
                    api.get('/analytics/metrics'),
                    api.get('/analytics/risks')
                ]);
                setMetrics(mRes.data);
                setRisks(rRes.data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) return <div className="p-8">Loading dashboard...</div>;

    // Prepare Chart Data (Lead Time)
    // Metrics are sorted DESC by day in backend, need ASC for chart
    const sortedMetrics = [...metrics].reverse();
    const labels = sortedMetrics.map(m => m.day);
    const data = {
        labels,
        datasets: [
            {
                label: 'Lead Time P85 (hours)',
                data: sortedMetrics.map(m => m.lead_time_p85),
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
            },
            {
                label: 'Throughput (PRs/day)',
                data: sortedMetrics.map(m => m.throughput),
                borderColor: 'rgb(53, 162, 235)',
                backgroundColor: 'rgba(53, 162, 235, 0.5)',
            },
        ],
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <Nav />
            <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <h1 className="text-2xl font-bold mb-4">Engineering Health Dashboard</h1>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Metrics Chart */}
                    <div className="bg-white p-6 rounded shadow">
                        <h2 className="text-lg font-medium mb-4">Trends</h2>
                        {metrics.length > 0 ? <Line data={data} /> : <p>No metrics available.</p>}
                    </div>

                    {/* Risks */}
                    <div className="bg-white p-6 rounded shadow">
                        <h2 className="text-lg font-medium mb-4 text-red-600">Active Risks</h2>
                        {risks.length === 0 ? (
                            <p className="text-green-600">No active risks detected.</p>
                        ) : (
                            <ul className="space-y-4">
                                {risks.map((risk, idx) => (
                                    <li key={idx} className="border-l-4 border-red-500 pl-4 py-2 bg-red-50">
                                        <div className="font-bold text-red-800">{risk.type} (Score: {risk.score.toFixed(2)})</div>
                                        <div className="text-sm text-red-700">{risk.explanation}</div>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                </div>

                {/* Metrics Table */}
                <div className="mt-6 bg-white p-6 rounded shadow overflow-x-auto">
                    <h2 className="text-lg font-medium mb-4">Daily Metrics</h2>
                    <table className="min-w-full divide-y divide-gray-200 text-sm">
                        <thead>
                            <tr>
                                <th className="px-4 py-2 text-left">Date</th>
                                <th className="px-4 py-2 text-left">Lead Time P85</th>
                                <th className="px-4 py-2 text-left">WIP</th>
                                <th className="px-4 py-2 text-left">Throughput</th>
                                <th className="px-4 py-2 text-left">Bug Ratio</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {metrics.map((m: any) => (
                                <tr key={m.id}>
                                    <td className="px-4 py-2">{m.day}</td>
                                    <td className="px-4 py-2">{m.lead_time_p85?.toFixed(1)}h</td>
                                    <td className="px-4 py-2">{m.wip}</td>
                                    <td className="px-4 py-2">{m.throughput?.toFixed(1)}</td>
                                    <td className="px-4 py-2">{(m.bug_ratio * 100).toFixed(1)}%</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
