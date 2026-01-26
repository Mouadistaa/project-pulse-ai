'use client';

import { useState } from 'react';
import api from '@/lib/api';
import { Nav } from '@/components/Nav';

export default function SimulationPage() {
    const [targetDate, setTargetDate] = useState('');
    const [backlogSize, setBacklogSize] = useState(10);
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    const handleSimulate = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await api.get('/forecast', {
                params: { target_date: targetDate, backlog_size: backlogSize }
            });
            setResult(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <Nav />
            <div className="max-w-2xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
                <h1 className="text-3xl font-bold mb-8">Delivery Simulation</h1>

                <div className="bg-white p-6 rounded shadow mb-8">
                    <h2 className="text-xl font-medium mb-4">Parameters</h2>
                    <form onSubmit={handleSimulate} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Backlog Size (Items)</label>
                            <input
                                type="number"
                                min="1"
                                value={backlogSize}
                                onChange={(e) => setBacklogSize(parseInt(e.target.value))}
                                className="mt-1 w-full border border-gray-300 rounded p-2"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Target Date</label>
                            <input
                                type="date"
                                value={targetDate}
                                onChange={(e) => setTargetDate(e.target.value)}
                                className="mt-1 w-full border border-gray-300 rounded p-2"
                                required
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-indigo-600 text-white p-3 rounded hover:bg-indigo-700 disabled:opacity-50"
                        >
                            {loading ? 'Running Monte Carlo Simulation...' : 'Run Simulation'}
                        </button>
                    </form>
                </div>

                {result && (
                    <div className="bg-white p-8 rounded shadow text-center">
                        <h3 className="text-lg font-medium text-gray-500 mb-2">Success Probability</h3>
                        <div className={`text-5xl font-bold ${result.probability >= 0.8 ? 'text-green-600' :
                                result.probability >= 0.5 ? 'text-yellow-600' :
                                    'text-red-600'
                            }`}>
                            {(result.probability * 100).toFixed(1)}%
                        </div>
                        <p className="mt-4 text-gray-600">
                            There is a {(result.probability * 100).toFixed(1)}% chance of completing {result.backlog_size} items by {result.target_date} based on historical throughput.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
