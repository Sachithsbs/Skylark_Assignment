import { useState, useEffect } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { 
  MessageSquare, 
  LayoutDashboard, 
  FileText, 
  Shield, 
  Menu, 
  X, 
  LogOut, 
  Plane,
  Wifi,
  RefreshCw
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getHealth } from '../services/api';

export const Layout = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const { user, logout } = useAuth();
  const location = useLocation();

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await getHealth();
        setIsOnline(true);
      } catch (e) {
        setIsOnline(false);
      }
    };
    
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { path: '/', label: 'Chat', icon: MessageSquare },
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/leadership', label: 'Leadership Report', icon: FileText },
    { path: '/quality', label: 'Data Quality', icon: Shield },
  ];

  const pageTitle = navItems.find(item => item.path === location.pathname)?.label || 'Skylark BI';

  return (
    <div className="flex h-screen overflow-hidden bg-surface-900">
      {/* Mobile sidebar overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-20 lg:hidden backdrop-blur-sm"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside 
        className={`fixed inset-y-0 left-0 z-30 w-64 bg-surface-800/90 backdrop-blur-xl border-r border-white/10 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="h-16 flex items-center px-6 border-b border-white/5">
          <Plane className="w-6 h-6 text-brand-500 mr-3" />
          <span className="text-lg font-bold text-white tracking-wide">Skylark BI</span>
          <button 
            className="ml-auto lg:hidden text-slate-400 hover:text-white"
            onClick={() => setIsSidebarOpen(false)}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto py-6 px-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={`flex items-center px-3 py-3 rounded-xl transition-all duration-200 group ${
                  isActive 
                    ? 'bg-brand-500/10 text-brand-400 border-l-2 border-brand-500 glow-blue' 
                    : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
                }`}
                onClick={() => setIsSidebarOpen(false)}
              >
                <Icon className={`w-5 h-5 mr-3 ${isActive ? 'text-brand-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
                <span className="font-medium text-sm">{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        <div className="p-4 border-t border-white/5">
          <div className="glass-card p-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-brand-600 to-cyan-500 flex items-center justify-center text-white font-bold text-sm">
                {user?.username.charAt(0).toUpperCase()}
              </div>
              <div>
                <p className="text-sm font-medium text-white">{user?.username}</p>
                <p className="text-xs text-slate-400 capitalize">{user?.role}</p>
              </div>
            </div>
            <button 
              onClick={logout}
              className="p-2 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-full overflow-hidden bg-mesh relative">
        {/* Topbar */}
        <header className="h-16 flex items-center justify-between px-4 lg:px-8 border-b border-white/5 glass-card rounded-none z-10 sticky top-0">
          <div className="flex items-center">
            <button 
              className="p-2 mr-3 lg:hidden text-slate-400 hover:text-white rounded-lg hover:bg-white/5"
              onClick={() => setIsSidebarOpen(true)}
            >
              <Menu className="w-5 h-5" />
            </button>
            <h2 className="text-lg font-semibold text-white">{pageTitle}</h2>
          </div>
          
          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 text-xs font-medium px-2.5 py-1 rounded-full border ${
              isOnline 
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
            }`}>
              <Wifi className="w-3 h-3" />
              {isOnline ? 'API Connected' : 'Disconnected'}
            </div>
            <button 
              onClick={() => window.location.reload()}
              className="p-2 text-slate-400 hover:text-brand-400 hover:bg-brand-500/10 rounded-lg transition-colors"
              title="Refresh"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </header>

        {/* Content area */}
        <div className="flex-1 overflow-auto p-4 lg:p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
};
