'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import { Nav } from '@/components/Nav';
import { formatDate } from '@/lib/utils'; // Assumed utils

export default function AlertsPage() {
    const [alerts, setAlerts] = useState<any[]>([]);

    useEffect(() => {
        fetchAlerts();
    }, []);

    const fetchAlerts = async () => {
        try {
            const res = await api.get('/alerts');
            setAlerts(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const handleAck = async (id: string) => {
        try {
            await api.post(`/alerts/${id}/ack`);
            fetchAlerts();
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <Nav />
            <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <h1 className="text-2xl font-bold mb-6">Alerts</h1>
                <div className="bg-white shadow overflow-hidden sm:rounded-md">
                    <ul className="divide-y divide-gray-200">
                        {alerts.length === 0 && <li className="p-4 text-gray-500">No alerts found.</li>}
                        {alerts.map((alert) => (
                            <li key={alert.id} className="p-4 flex items-center justify-between hover:bg-gray-50">
                                <div>
                                    <div className="flex items-center">
                                        <span className={`px-2 py-1 text-xs font-bold rounded-full mr-2 ${alert.severity === 'HIGH' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                                            }`}>
                                            {alert.severity}
                                        </span>
                                        <p className="text-sm font-medium text-blue-600 truncate">{alert.title}</p>
                                    </div>
                                    <div className="mt-2 text-sm text-gray-500">
                                        <p>{alert.history}</p>
                                    </div>
                                </div>
                                <div className="flex items-center space-x-4">
                                    <span className={`text-sm ${alert.status === 'NEW' ? 'font-bold text-green-600' : 'text-gray-400'}`}>
                                        {alert.status}
                                    </span>
                                    {alert.status === 'NEW' && (
                                        <button
                                            onClick={() => handleAck(alert.id)}
                                            className="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded hover:bg-blue-200"
                                        >
                                            Acknowledge
                                        </button>
                                    )}
                                </div>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
}
