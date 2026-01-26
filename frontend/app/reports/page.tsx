'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import api from '@/lib/api';
import { Nav } from '@/components/Nav';

export default function ReportsPage() {
    const [reports, setReports] = useState<any[]>([]);
    const [generating, setGenerating] = useState(false);

    useEffect(() => {
        fetchReports();
    }, []);

    const fetchReports = async () => {
        try {
            const res = await api.get('/reports');
            setReports(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const handleGenerate = async () => {
        setGenerating(true);
        try {
            // Just hardcoded period for demo
            const period = new Date().toISOString().split('T')[0];
            await api.post(`/reports/generate?period=${period}`);
            fetchReports();
        } catch (err) {
            console.error(err);
        } finally {
            setGenerating(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <Nav />
            <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold">Reports</h1>
                    <button
                        onClick={handleGenerate}
                        disabled={generating}
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
                    >
                        {generating ? 'Generating...' : 'Generate New Report'}
                    </button>
                </div>

                <div className="grid gap-4">
                    {reports.map((report) => (
                        <Link key={report.id} href={`/reports/${report.id}`} className="block">
                            <div className="bg-white p-6 rounded shadow hover:shadow-md transition">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h3 className="text-lg font-medium text-gray-900">Report: {report.period}</h3>
                                        <p className="text-sm text-gray-500 mt-1">Generated: {new Date(report.created_at).toLocaleString()}</p>
                                    </div>
                                    <span className={`px-2 py-1 text-xs font-bold rounded-full ${report.status === 'SENT' ? 'bg-green-100 text-green-800' :
                                            report.status === 'APPROVED' ? 'bg-blue-100 text-blue-800' :
                                                'bg-gray-100 text-gray-800'
                                        }`}>
                                        {report.status}
                                    </span>
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>
            </div>
        </div>
    );
}
