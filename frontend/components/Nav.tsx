'use client';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { removeToken } from '@/lib/auth';

const links = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/integrations', label: 'Integrations' },
    { href: '/alerts', label: 'Alerts' },
    { href: '/reports', label: 'Reports' },
    { href: '/simulation', label: 'Simulation' },
];

export function Nav() {
    const pathname = usePathname();
    const router = useRouter();

    const handleLogout = () => {
        removeToken();
        router.push('/login');
    };

    return (
        <nav className="bg-white border-b border-gray-200 px-4 py-2.5 flex justify-between items-center">
            <div className="flex items-center space-x-6">
                <span className="font-bold text-xl text-blue-600">Pulse AI</span>
                {links.map((link) => (
                    <Link
                        key={link.href}
                        href={link.href}
                        className={`text-sm font-medium ${pathname === link.href ? 'text-blue-600' : 'text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        {link.label}
                    </Link>
                ))}
            </div>
            <button onClick={handleLogout} className="text-sm text-red-500 hover:text-red-700">
                Logout
            </button>
        </nav>
    );
}
