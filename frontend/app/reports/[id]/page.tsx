'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import api from '@/lib/api';
import { Nav } from '@/components/Nav';
import ReactMarkdown from 'react-markdown'; // Assuming we might add this later, but for now just raw or simple

export default function ReportDetailPage() {
    const { id } = useParams();
    const router = useRouter();
    const [report, setReport] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (id) fetchReport();
    }, [id]);

    const fetchReport = async () => {
        try {
            // We didn't make a GET /reports/{id} endpoint in plan!
            // But we have LIST. Let's filter client side for MVP or fix backend?
            // Actually best to fix backend or just iterate list.
            // Let's assume we can fetch list and find it for now to save backend task.
            const res = await api.get('/reports');
            const r = res.data.find((x: any) => x.id === id);
            setReport(r);
        } catch (err) {
            console.error(err);
        }
    };

    const handleAction = async (action: 'approve' | 'send') => {
        setLoading(true);
        try {
            await api.post(`/reports/${id}/${action}`);
            fetchReport();
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (!report) return <div>Loading...</div>;

    return (
        <div className="min-h-screen bg-gray-50">
            <Nav />
            <div className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
                <button onClick={() => router.back()} className="text-blue-600 mb-4 hover:underline">&larr; Back to Reports</button>

                <div className="bg-white p-8 rounded shadow">
                    <div className="flex justify-between items-center border-b pb-4 mb-6">
                        <h1 className="text-2xl font-bold">Engineering Report ({report.period})</h1>
                        <div className="space-x-2">
                            {report.status === 'DRAFT' && (
                                <button
                                    onClick={() => handleAction('approve')}
                                    disabled={loading}
                                    className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
                                >
                                    Approve
                                </button>
                            )}
                            {report.status === 'APPROVED' && (
                                <button
                                    onClick={() => handleAction('send')}
                                    disabled={loading}
                                    className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 disabled:opacity-50"
                                >
                                    Send
                                </button>
                            )}
                            <span className="px-3 py-2 bg-gray-100 rounded font-mono text-sm">
                                {report.status}
                            </span>
                        </div>
                    </div>

                    <div className="prose max-w-none whitespace-pre-wrap font-sans text-gray-800">
                        {report.content}
                    </div>

                    <div className="mt-8 pt-4 border-t text-sm text-gray-400">
                        Source Metadata: {JSON.stringify(report.sources_json)}
                    </div>
                </div>
            </div>
        </div>
    );
}
