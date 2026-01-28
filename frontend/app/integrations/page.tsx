'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import { Nav } from '@/components/Nav';

interface Integration {
    id: string;
    type: string;
    name: string;
    status: string;
    config: Record<string, any>;
}

export default function IntegrationsPage() {
    const [integrations, setIntegrations] = useState<Integration[]>([]);
    const [loading, setLoading] = useState(true);
    const [syncing, setSyncing] = useState(false);
    const [syncResult, setSyncResult] = useState<string | null>(null);

    useEffect(() => {
        fetchIntegrations();
    }, []);

    const fetchIntegrations = async () => {
        try {
            const response = await api.get('/integrations/');
            setIntegrations(response.data);
        } catch (err) {
            console.error('Failed to fetch integrations:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleSync = async () => {
        setSyncing(true);
        setSyncResult(null);
        try {
            const response = await api.post('/jobs/sync');
            setSyncResult(`Sync job queued: ${response.data.job_id}`);
        } catch (err) {
            setSyncResult('Failed to start sync job');
            console.error(err);
        } finally {
            setSyncing(false);
        }
    };

    const getStatusColor = (status: string) => {
        switch (status.toUpperCase()) {
            case 'ACTIVE':
                return 'bg-green-100 text-green-800';
            case 'DISABLED':
                return 'bg-gray-100 text-gray-800';
            default:
                return 'bg-yellow-100 text-yellow-800';
        }
    };

    const getTypeIcon = (type: string) => {
        switch (type.toUpperCase()) {
            case 'GITHUB':
                return (
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                        <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                    </svg>
                );
            case 'TRELLO':
                return (
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M21 3H3C1.9 3 1 3.9 1 5v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM10 17H6c-.55 0-1-.45-1-1V8c0-.55.45-1 1-1h4c.55 0 1 .45 1 1v8c0 .55-.45 1-1 1zm8-4h-4c-.55 0-1-.45-1-1V8c0-.55.45-1 1-1h4c.55 0 1 .45 1 1v4c0 .55-.45 1-1 1z" />
                    </svg>
                );
            default:
                return (
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                );
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50">
                <Nav />
                <div className="p-8">Loading integrations...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <Nav />
            <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold">Integrations</h1>
                    <button
                        onClick={handleSync}
                        disabled={syncing}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {syncing ? 'Syncing...' : 'Sync Now'}
                    </button>
                </div>

                {syncResult && (
                    <div className="mb-4 p-3 bg-blue-50 text-blue-800 rounded-lg">
                        {syncResult}
                    </div>
                )}

                {integrations.length === 0 ? (
                    <div className="bg-white p-8 rounded-lg shadow text-center text-gray-500">
                        No integrations configured. Run the seed script to create demo integrations.
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {integrations.map((integration) => (
                            <div
                                key={integration.id}
                                className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow"
                            >
                                <div className="flex items-center space-x-4">
                                    <div className="text-gray-700">
                                        {getTypeIcon(integration.type)}
                                    </div>
                                    <div className="flex-1">
                                        <h3 className="font-semibold text-lg">{integration.name}</h3>
                                        <p className="text-sm text-gray-500">{integration.type}</p>
                                    </div>
                                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(integration.status)}`}>
                                        {integration.status}
                                    </span>
                                </div>
                                {integration.config && Object.keys(integration.config).length > 0 && (
                                    <div className="mt-4 pt-4 border-t border-gray-100">
                                        <p className="text-xs text-gray-400 uppercase tracking-wide mb-2">Configuration</p>
                                        <pre className="text-xs text-gray-600 bg-gray-50 p-2 rounded overflow-x-auto">
                                            {JSON.stringify(integration.config, null, 2)}
                                        </pre>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                <div className="mt-8 bg-white p-6 rounded-lg shadow">
                    <h2 className="text-lg font-semibold mb-4">Supported Integrations</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="flex items-center space-x-3 p-4 border rounded-lg">
                            <div className="text-gray-700">
                                {getTypeIcon('GITHUB')}
                            </div>
                            <div>
                                <h3 className="font-medium">GitHub</h3>
                                <p className="text-sm text-gray-500">Pull requests, repositories, code reviews</p>
                            </div>
                        </div>
                        <div className="flex items-center space-x-3 p-4 border rounded-lg">
                            <div className="text-gray-700">
                                {getTypeIcon('TRELLO')}
                            </div>
                            <div>
                                <h3 className="font-medium">Trello</h3>
                                <p className="text-sm text-gray-500">Boards, cards, workflow tracking</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
