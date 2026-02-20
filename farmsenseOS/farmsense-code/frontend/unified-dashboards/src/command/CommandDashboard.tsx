import { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  Users,
  TrendingUp,
  Settings,
  LogOut,
  Building2,
  DollarSign,
  Award,
  BarChart3,
  CheckCircle,
  Search,
  Plus,
  Handshake,
  ClipboardList,
  Target,
  Map,
  FileText,
  FolderOpen,
  UserPlus,
  Edit3,
  Trash2,
  X,
  Save,
  Zap,
  RefreshCw,
  Calendar,
  
} from 'lucide-react';
import { removeApiKey } from '../shared/api';
import Login from './Login';

// Types
interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  organization: string;
  status: 'active' | 'pending' | 'suspended';
  lastActive: string;
}

interface Task {
  id: string;
  title: string;
  status: 'backlog' | 'todo' | 'in_progress' | 'in_review' | 'done';
  priority: 'low' | 'medium' | 'high' | 'critical';
  assignee?: string;
  dueDate?: string;
  category?: string;
}

interface DailyGoal {
  id: string;
  title: string;
  isCompleted: boolean;
  priority: 'low' | 'medium' | 'high' | 'critical';
}

interface RoadmapItem {
  id: string;
  title: string;
  category: string;
  targetQuarter: string;
  progress: number;
  status: string;
}

interface Employee {
  id: string;
  name: string;
  email: string;
  department: string;
  jobTitle: string;
  status: string;
  startDate: string;
  manager?: string;
}

interface FinancialRecord {
  id: string;
  category: string;
  amount: number;
  description: string;
  date: string;
  isForecast: boolean;
}

interface Meeting {
  id: string;
  title: string;
  type: 'standup' | 'weekly' | 'monthly' | 'quarterly' | 'ad_hoc';
  date: string;
  attendees: string[];
  agenda: string[];
  notes: string;
  actionItems: { task: string; assignee: string; dueDate: string }[];
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
}

const mockUsers: User[] = [
  { id: '1', name: 'John Doe', email: 'john@farm.com', role: 'Farmer', organization: 'Doe Farms', status: 'active', lastActive: '2 min ago' },
  { id: '2', name: 'Jane Smith', email: 'jane@agri.com', role: 'Investor', organization: 'AgriVentures', status: 'active', lastActive: '1 hour ago' },
  { id: '3', name: 'Mike Johnson', email: 'mike@gov.org', role: 'Auditor', organization: 'SLV Agency', status: 'active', lastActive: '3 hours ago' },
  { id: '4', name: 'Sarah Lee', email: 'sarah@research.edu', role: 'Researcher', organization: 'State University', status: 'pending', lastActive: 'Never' },
  { id: '5', name: 'Tom Wilson', email: 'tom@partner.com', role: 'Partner', organization: 'Irritech', status: 'active', lastActive: '5 min ago' },
];

const mockTasks: Task[] = [
  { id: '1', title: 'Deploy new sensor firmware', status: 'in_progress', priority: 'high', assignee: 'Engineering Team', dueDate: '2026-02-20', category: 'engineering' },
  { id: '2', title: 'Q1 Financial report', status: 'todo', priority: 'critical', assignee: 'Finance', dueDate: '2026-03-01', category: 'finance' },
  { id: '3', title: 'Update compliance documentation', status: 'done', priority: 'medium', assignee: 'Legal', category: 'legal' },
  { id: '4', title: 'Investor pitch deck', status: 'in_review', priority: 'high', assignee: 'CEO', dueDate: '2026-02-25', category: 'business' },
];

const mockDailyGoals: DailyGoal[] = [
  { id: '1', title: 'Review sensor data from Field A', isCompleted: true, priority: 'high' },
  { id: '2', title: 'Call with potential investor', isCompleted: false, priority: 'critical' },
  { id: '3', title: 'Update roadmap for Q2', isCompleted: false, priority: 'medium' },
  { id: '4', title: 'Team standup meeting', isCompleted: true, priority: 'low' },
];

const mockRoadmap: RoadmapItem[] = [
  { id: '1', title: 'Mobile app launch', category: 'Product', targetQuarter: '2026-Q2', progress: 65, status: 'in_progress' },
  { id: '2', title: 'AI-powered irrigation predictions', category: 'Engineering', targetQuarter: '2026-Q3', progress: 30, status: 'in_progress' },
  { id: '3', title: 'Series A fundraising', category: 'Business', targetQuarter: '2026-Q2', progress: 80, status: 'in_progress' },
  { id: '4', title: 'SLV 2026 Full Compliance', category: 'Operations', targetQuarter: '2026-Q4', progress: 45, status: 'in_progress' },
];

const mockEmployees: Employee[] = [
  { id: '1', name: 'Alex Chen', email: 'alex@farmsense.io', department: 'Engineering', jobTitle: 'Senior Software Engineer', status: 'active', startDate: '2024-01-15', manager: 'CTO' },
  { id: '2', name: 'Maria Garcia', email: 'maria@farmsense.io', department: 'Product', jobTitle: 'Product Manager', status: 'active', startDate: '2024-03-01' },
  { id: '3', name: 'James Wilson', email: 'james@farmsense.io', department: 'Sales', jobTitle: 'Account Executive', status: 'onboarding', startDate: '2026-02-01' },
];

const mockFinancials: FinancialRecord[] = [
  { id: '1', category: 'Revenue', amount: 125000, description: 'Enterprise customer - annual contract', date: '2026-02-01', isForecast: false },
  { id: '2', category: 'Expense', amount: 45000, description: 'AWS infrastructure', date: '2026-02-01', isForecast: false },
  { id: '3', category: 'Payroll', amount: 85000, description: 'February salaries', date: '2026-02-15', isForecast: false },
  { id: '4', category: 'Revenue', amount: 150000, description: 'Q1 projected new sales', date: '2026-03-31', isForecast: true },
];

const mockMeetings: Meeting[] = [
  {
    id: '1',
    title: 'Daily Standup - Engineering',
    type: 'standup',
    date: '2026-02-16T09:00:00',
    attendees: ['Alex Chen', 'Maria Garcia', 'CTO'],
    agenda: ['Yesterday\'s progress', 'Today\'s goals', 'Blockers'],
    notes: '',
    actionItems: [],
    status: 'scheduled'
  },
  {
    id: '2',
    title: 'Weekly Leadership Review',
    type: 'weekly',
    date: '2026-02-17T14:00:00',
    attendees: ['CEO', 'COO', 'CTO', 'CFO'],
    agenda: ['KPI Review', 'Roadmap Progress', 'Cross-functional Updates', 'Risk Register'],
    notes: '',
    actionItems: [],
    status: 'scheduled'
  },
  {
    id: '3',
    title: 'Monthly All-Hands',
    type: 'monthly',
    date: '2026-02-28T10:00:00',
    attendees: ['All Staff'],
    agenda: ['Company Updates', 'Department Highlights', 'Q&A', 'Celebrations'],
    notes: '',
    actionItems: [],
    status: 'scheduled'
  }
];

const CommandDashboard = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [userFilter, setUserFilter] = useState('all');
  const [dailyGoals, setDailyGoals] = useState(mockDailyGoals);
  const [tasks] = useState(mockTasks);
  const [showAddGoal, setShowAddGoal] = useState(false);
  const [_showAddTask, _setShowAddTask] = useState(false);
  const [newGoalTitle, setNewGoalTitle] = useState('');
  const [_newTaskTitle, _setNewTaskTitle] = useState('');

  useEffect(() => {
    // Load data from API
    // api.getOperationsDashboard().then(setDashboardData);
  }, []);

  const toggleGoal = (id: string) => {
    setDailyGoals(goals => goals.map(g => 
      g.id === id ? { ...g, isCompleted: !g.isCompleted } : g
    ));
  };

  const addGoal = () => {
    if (newGoalTitle.trim()) {
      setDailyGoals([...dailyGoals, {
        id: Date.now().toString(),
        title: newGoalTitle,
        isCompleted: false,
        priority: 'medium'
      }]);
      setNewGoalTitle('');
      setShowAddGoal(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-emerald-500/20 text-emerald-400';
      case 'pending': return 'bg-amber-500/20 text-amber-400';
      case 'suspended': return 'bg-red-500/20 text-red-400';
      default: return 'bg-slate-500/20 text-slate-400';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-500/20 text-red-400';
      case 'high': return 'bg-orange-500/20 text-orange-400';
      case 'medium': return 'bg-amber-500/20 text-amber-400';
      default: return 'bg-slate-500/20 text-slate-400';
    }
  };

  const getTaskStatusColor = (status: string) => {
    switch (status) {
      case 'done': return 'bg-emerald-500/20 text-emerald-400';
      case 'in_progress': return 'bg-blue-500/20 text-blue-400';
      case 'in_review': return 'bg-purple-500/20 text-purple-400';
      case 'todo': return 'bg-amber-500/20 text-amber-400';
      default: return 'bg-slate-500/20 text-slate-400';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'daily', label: 'Daily Goals', icon: Target },
    { id: 'tasks', label: 'Tasks & Todos', icon: ClipboardList },
    { id: 'meetings', label: 'Meetings', icon: Calendar },
    { id: 'roadmap', label: 'Roadmap', icon: Map },
    { id: 'users', label: 'Users & Access', icon: Users },
    { id: 'employees', label: 'Team', icon: UserPlus },
    { id: 'financials', label: 'Financials', icon: DollarSign },
    { id: 'investors', label: 'Investors', icon: TrendingUp },
    { id: 'grants', label: 'Grants', icon: Award },
    { id: 'partners', label: 'Partners', icon: Handshake },
    { id: 'documents', label: 'Documents', icon: FolderOpen },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'system', label: 'System', icon: Zap },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  if (!isAuthenticated) {
    return <Login onLogin={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="min-h-screen bg-slate-950 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
              <Building2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">Command</h1>
              <p className="text-xs text-slate-500">Center</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all text-left ${
                activeTab === item.id
                  ? 'bg-indigo-500/10 text-indigo-400'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium text-sm">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-800">
          <button
            onClick={() => { removeApiKey(); setIsAuthenticated(false); }}
            className="w-full flex items-center gap-3 px-4 py-2 text-red-400 hover:bg-red-500/10 rounded-xl transition-colors"
          >
            <LogOut className="w-5 h-5" />
            <span className="font-medium text-sm">Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {/* Header */}
        <header className="sticky top-0 z-40 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800 px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white capitalize">{activeTab.replace('-', ' ')}</h2>
            <div className="flex items-center gap-4">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="text"
                  placeholder="Search..."
                  className="bg-slate-900 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 w-64"
                />
              </div>
              <button className="w-8 h-8 bg-indigo-500 rounded-full flex items-center justify-center text-white font-bold">
                A
              </button>
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="p-6">
          {/* OVERVIEW TAB */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Key Metrics */}
              <div className="grid grid-cols-4 gap-4">
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
                  <p className="text-slate-400 text-sm">Active Users</p>
                  <p className="text-2xl font-bold text-white mt-1">15,420</p>
                  <span className="text-emerald-400 text-xs">+15.4%</span>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
                  <p className="text-slate-400 text-sm">Daily Goals</p>
                  <p className="text-2xl font-bold text-white mt-1">{dailyGoals.filter(g => g.isCompleted).length}/{dailyGoals.length}</p>
                  <span className="text-emerald-400 text-xs">{Math.round((dailyGoals.filter(g => g.isCompleted).length / dailyGoals.length) * 100)}% done</span>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
                  <p className="text-slate-400 text-sm">Tasks In Progress</p>
                  <p className="text-2xl font-bold text-white mt-1">{tasks.filter(t => t.status === 'in_progress').length}</p>
                  <span className="text-amber-400 text-xs">{tasks.filter(t => t.priority === 'critical').length} critical</span>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
                  <p className="text-slate-400 text-sm">Runway</p>
                  <p className="text-2xl font-bold text-white mt-1">18 mo</p>
                  <span className="text-emerald-400 text-xs">Series A in progress</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6">
                {/* Today's Goals */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-white font-bold flex items-center gap-2">
                      <Target className="w-5 h-5 text-indigo-400" />
                      Today's Goals
                    </h3>
                    <button 
                      onClick={() => setShowAddGoal(true)}
                      className="text-indigo-400 hover:text-indigo-300"
                    >
                      <Plus className="w-5 h-5" />
                    </button>
                  </div>
                  <div className="space-y-2">
                    {dailyGoals.map((goal) => (
                      <div key={goal.id} className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-xl">
                        <button 
                          onClick={() => toggleGoal(goal.id)}
                          className={`w-5 h-5 rounded border flex items-center justify-center transition-colors ${
                            goal.isCompleted ? 'bg-emerald-500 border-emerald-500' : 'border-slate-600'
                          }`}
                        >
                          {goal.isCompleted && <CheckCircle className="w-3 h-3 text-white" />}
                        </button>
                        <span className={`flex-1 text-sm ${goal.isCompleted ? 'text-slate-500 line-through' : 'text-white'}`}>
                          {goal.title}
                        </span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${getPriorityColor(goal.priority)}`}>
                          {goal.priority}
                        </span>
                      </div>
                    ))}
                    {showAddGoal && (
                      <div className="flex items-center gap-2 p-3 bg-slate-800 rounded-xl">
                        <input
                          type="text"
                          value={newGoalTitle}
                          onChange={(e) => setNewGoalTitle(e.target.value)}
                          placeholder="New goal..."
                          className="flex-1 bg-transparent text-white text-sm focus:outline-none"
                          onKeyPress={(e) => e.key === 'Enter' && addGoal()}
                        />
                        <button onClick={addGoal} className="text-emerald-400">
                          <Save className="w-4 h-4" />
                        </button>
                        <button onClick={() => setShowAddGoal(false)} className="text-slate-400">
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Priority Tasks */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-white font-bold flex items-center gap-2">
                      <ClipboardList className="w-5 h-5 text-indigo-400" />
                      Priority Tasks
                    </h3>
                    <button className="text-indigo-400 hover:text-indigo-300">
                      <Plus className="w-5 h-5" />
                    </button>
                  </div>
                  <div className="space-y-2">
                    {tasks.filter(t => t.priority === 'critical' || t.priority === 'high').map((task) => (
                      <div key={task.id} className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-xl">
                        <div className={`w-2 h-2 rounded-full ${
                          task.status === 'done' ? 'bg-emerald-500' :
                          task.status === 'in_progress' ? 'bg-blue-500' : 'bg-amber-500'
                        }`} />
                        <span className="flex-1 text-sm text-white">{task.title}</span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${getTaskStatusColor(task.status)}`}>
                          {task.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* DAILY GOALS TAB */}
          {activeTab === 'daily' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <h3 className="text-white font-bold">Daily Goals Management</h3>
                  <span className="text-slate-400 text-sm">{new Date().toLocaleDateString()}</span>
                </div>
                <button 
                  onClick={() => setShowAddGoal(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg"
                >
                  <Plus className="w-4 h-4" />
                  Add Goal
                </button>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <p className="text-slate-400 text-sm">Total Goals</p>
                  <p className="text-3xl font-bold text-white mt-1">{dailyGoals.length}</p>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <p className="text-slate-400 text-sm">Completed</p>
                  <p className="text-3xl font-bold text-emerald-400 mt-1">{dailyGoals.filter(g => g.isCompleted).length}</p>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <p className="text-slate-400 text-sm">Completion Rate</p>
                  <p className="text-3xl font-bold text-white mt-1">
                    {Math.round((dailyGoals.filter(g => g.isCompleted).length / dailyGoals.length) * 100)}%
                  </p>
                </div>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                <div className="space-y-3">
                  {dailyGoals.map((goal) => (
                    <div key={goal.id} className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-xl">
                      <button 
                        onClick={() => toggleGoal(goal.id)}
                        className={`w-6 h-6 rounded-lg border flex items-center justify-center transition-colors ${
                          goal.isCompleted ? 'bg-emerald-500 border-emerald-500' : 'border-slate-600 hover:border-indigo-500'
                        }`}
                      >
                        {goal.isCompleted && <CheckCircle className="w-4 h-4 text-white" />}
                      </button>
                      <div className="flex-1">
                        <p className={`text-white ${goal.isCompleted ? 'line-through text-slate-500' : ''}`}>
                          {goal.title}
                        </p>
                      </div>
                      <span className={`text-xs px-3 py-1 rounded-full ${getPriorityColor(goal.priority)}`}>
                        {goal.priority}
                      </span>
                      <button className="text-slate-400 hover:text-red-400">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TASKS TAB */}
          {activeTab === 'tasks' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {['all', 'backlog', 'in_progress', 'done'].map((filter) => (
                    <button
                      key={filter}
                      className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-300 text-sm hover:bg-slate-800 capitalize"
                    >
                      {filter.replace('_', ' ')}
                    </button>
                  ))}
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg">
                  <Plus className="w-4 h-4" />
                  New Task
                </button>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
                <table className="w-full">
                  <thead className="bg-slate-800/50">
                    <tr>
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">Task</th>
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">Assignee</th>
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">Status</th>
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">Priority</th>
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">Due Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tasks.map((task) => (
                      <tr key={task.id} className="border-t border-slate-800">
                        <td className="p-4">
                          <p className="text-white font-medium">{task.title}</p>
                          <p className="text-slate-500 text-sm capitalize">{task.category}</p>
                        </td>
                        <td className="p-4 text-slate-300">{task.assignee}</td>
                        <td className="p-4">
                          <span className={`text-xs px-2 py-1 rounded-full ${getTaskStatusColor(task.status)}`}>
                            {task.status.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="p-4">
                          <span className={`text-xs px-2 py-1 rounded-full ${getPriorityColor(task.priority)}`}>
                            {task.priority}
                          </span>
                        </td>
                        <td className="p-4 text-slate-400">{task.dueDate}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* MEETINGS TAB */}
          {activeTab === 'meetings' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {['all', 'standup', 'weekly', 'monthly', 'quarterly'].map((filter) => (
                    <button key={filter} className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-300 text-sm hover:bg-slate-800 capitalize">
                      {filter}
                    </button>
                  ))}
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg">
                  <Plus className="w-4 h-4" />
                  Schedule Meeting
                </button>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <p className="text-slate-400 text-sm">Today</p>
                  <p className="text-3xl font-bold text-white mt-1">3</p>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <p className="text-slate-400 text-sm">This Week</p>
                  <p className="text-3xl font-bold text-emerald-400 mt-1">12</p>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <p className="text-slate-400 text-sm">Completion Rate</p>
                  <p className="text-3xl font-bold text-white mt-1">94%</p>
                </div>
              </div>

              <div className="space-y-3">
                {mockMeetings.map((meeting) => (
                  <div key={meeting.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h4 className="text-white font-bold">{meeting.title}</h4>
                          <span className="text-xs px-2 py-1 bg-blue-500/20 text-blue-400 rounded-full">{meeting.status}</span>
                          <span className="text-xs px-2 py-1 bg-slate-800 rounded-full text-slate-400 capitalize">{meeting.type}</span>
                        </div>
                        <p className="text-slate-400 text-sm mb-2">{new Date(meeting.date).toLocaleString()}</p>
                        <p className="text-slate-500 text-sm mb-3">Attendees: {meeting.attendees.join(', ')}</p>
                        <div className="flex flex-wrap gap-2">
                          {meeting.agenda.map((item, i) => (
                            <span key={i} className="text-xs px-3 py-1 bg-slate-800 rounded-full text-slate-300">{item}</span>
                          ))}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm">Join</button>
                        <button className="px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg text-sm">Notes</button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ROADMAP TAB */}
          {activeTab === 'roadmap' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-white font-bold">Strategic Roadmap</h3>
                <button className="flex items-center gap-2 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg">
                  <Plus className="w-4 h-4" />
                  Add Roadmap Item
                </button>
              </div>

              <div className="space-y-4">
                {mockRoadmap.map((item) => (
                  <div key={item.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <div className="flex items-center gap-3 mb-2">
                          <h4 className="text-white font-bold text-lg">{item.title}</h4>
                          <span className="text-xs px-2 py-1 bg-slate-800 rounded-full text-slate-400">
                            {item.category}
                          </span>
                        </div>
                        <p className="text-slate-400 text-sm">Target: {item.targetQuarter}</p>
                      </div>
                      <span className={`text-xs px-3 py-1 rounded-full ${getTaskStatusColor(item.status)}`}>
                        {item.status.replace('_', ' ')}
                      </span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-3 mb-2">
                      <div 
                        className="bg-gradient-to-r from-indigo-500 to-purple-500 h-3 rounded-full transition-all"
                        style={{ width: `${item.progress}%` }}
                      />
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-400">{item.progress}% complete</span>
                      <div className="flex items-center gap-2">
                        <button className="text-indigo-400 hover:text-indigo-300 text-xs">Update Progress</button>
                        <button className="text-slate-400 hover:text-white">
                          <Edit3 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* EMPLOYEES TAB */}
          {activeTab === 'employees' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <button className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-300 text-sm">
                    All Departments
                  </button>
                  <button className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-300 text-sm">
                    Active Only
                  </button>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg">
                  <UserPlus className="w-4 h-4" />
                  Add Employee
                </button>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <p className="text-slate-400 text-sm">Total Employees</p>
                  <p className="text-3xl font-bold text-white mt-1">{mockEmployees.length}</p>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <p className="text-slate-400 text-sm">Active</p>
                  <p className="text-3xl font-bold text-emerald-400 mt-1">
                    {mockEmployees.filter(e => e.status === 'active').length}
                  </p>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <p className="text-slate-400 text-sm">Onboarding</p>
                  <p className="text-3xl font-bold text-amber-400 mt-1">
                    {mockEmployees.filter(e => e.status === 'onboarding').length}
                  </p>
                </div>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
                <table className="w-full">
                  <thead className="bg-slate-800/50">
                    <tr>
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">Employee</th>
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">Department</th>
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">Role</th>
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">Status</th>
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">Start Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mockEmployees.map((emp) => (
                      <tr key={emp.id} className="border-t border-slate-800">
                        <td className="p-4">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-indigo-500/20 rounded-full flex items-center justify-center text-indigo-400 font-bold text-sm">
                              {emp.name.charAt(0)}
                            </div>
                            <div>
                              <p className="text-white font-medium">{emp.name}</p>
                              <p className="text-slate-500 text-sm">{emp.email}</p>
                            </div>
                          </div>
                        </td>
                        <td className="p-4 text-slate-300">{emp.department}</td>
                        <td className="p-4 text-slate-300">{emp.jobTitle}</td>
                        <td className="p-4">
                          <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(emp.status)}`}>
                            {emp.status}
                          </span>
                        </td>
                        <td className="p-4 text-slate-400">{emp.startDate}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* FINANCIALS TAB */}
          {activeTab === 'financials' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-white font-bold">Financial Management</h3>
                <button className="flex items-center gap-2 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg">
                  <Plus className="w-4 h-4" />
                  Add Transaction
                </button>
              </div>

              <div className="grid grid-cols-4 gap-4">
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <p className="text-slate-400 text-sm">Total Revenue (YTD)</p>
                  <p className="text-2xl font-bold text-emerald-400 mt-1">$1.2M</p>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <p className="text-slate-400 text-sm">Total Expenses (YTD)</p>
                  <p className="text-2xl font-bold text-red-400 mt-1">$890K</p>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <p className="text-slate-400 text-sm">Net Income</p>
                  <p className="text-2xl font-bold text-white mt-1">$310K</p>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <p className="text-slate-400 text-sm">Burn Rate</p>
                  <p className="text-2xl font-bold text-amber-400 mt-1">$85K/mo</p>
                </div>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
                <table className="w-full">
                  <thead className="bg-slate-800/50">
                    <tr>
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">Date</th>
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">Category</th>
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">Description</th>
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">Amount</th>
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">Type</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mockFinancials.map((record) => (
                      <tr key={record.id} className="border-t border-slate-800">
                        <td className="p-4 text-slate-400">{record.date}</td>
                        <td className="p-4 text-slate-300">{record.category}</td>
                        <td className="p-4 text-white">{record.description}</td>
                        <td className={`p-4 font-medium ${
                          record.category === 'Revenue' ? 'text-emerald-400' : 'text-red-400'
                        }`}>
                          {record.category === 'Revenue' ? '+' : '-'}{formatCurrency(record.amount)}
                        </td>
                        <td className="p-4">
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            record.isForecast ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'
                          }`}>
                            {record.isForecast ? 'Forecast' : 'Actual'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* USERS TAB */}
          {activeTab === 'users' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {['all', 'farmers', 'investors', 'auditors', 'partners'].map((filter) => (
                    <button
                      key={filter}
                      onClick={() => setUserFilter(filter)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        userFilter === filter
                          ? 'bg-indigo-500 text-white'
                          : 'bg-slate-900 text-slate-400 hover:text-white'
                      }`}
                    >
                      {filter.charAt(0).toUpperCase() + filter.slice(1)}
                    </button>
                  ))}
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg">
                  <Plus className="w-4 h-4" />
                  Add User
                </button>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-800">
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">User</th>
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">Role</th>
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">Organization</th>
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">Status</th>
                      <th className="text-left p-4 text-slate-400 text-sm font-medium">Last Active</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mockUsers.map((user) => (
                      <tr key={user.id} className="border-b border-slate-800 hover:bg-slate-800/50">
                        <td className="p-4">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-indigo-500/20 rounded-full flex items-center justify-center text-indigo-400 font-bold text-sm">
                              {user.name.charAt(0)}
                            </div>
                            <div>
                              <p className="text-white font-medium">{user.name}</p>
                              <p className="text-slate-500 text-sm">{user.email}</p>
                            </div>
                          </div>
                        </td>
                        <td className="p-4 text-slate-300">{user.role}</td>
                        <td className="p-4 text-slate-300">{user.organization}</td>
                        <td className="p-4">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(user.status)}`}>
                            {user.status}
                          </span>
                        </td>
                        <td className="p-4 text-slate-400 text-sm">{user.lastActive}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* DOCUMENTS TAB */}
          {activeTab === 'documents' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {['All', 'Strategy', 'Tactical', 'Policies', 'Handbooks'].map((filter) => (
                    <button key={filter} className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-300 text-sm">
                      {filter}
                    </button>
                  ))}
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg">
                  <Plus className="w-4 h-4" />
                  New Document
                </button>
              </div>

              <div className="grid grid-cols-3 gap-4">
                {[
                  { title: '2026 Strategic Plan', type: 'Strategy', author: 'CEO', updated: '2 days ago' },
                  { title: 'Q1 OKRs', type: 'Tactical', author: 'COO', updated: '1 week ago' },
                  { title: 'Employee Handbook', type: 'Handbook', author: 'HR', updated: '1 month ago' },
                  { title: 'Engineering Playbook', type: 'Policies', author: 'CTO', updated: '2 weeks ago' },
                  { title: 'Sales Playbook', type: 'Policies', author: 'CRO', updated: '3 days ago' },
                  { title: 'Security Policy', type: 'Policies', author: 'CTO', updated: '1 week ago' },
                ].map((doc, i) => (
                  <div key={i} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 cursor-pointer">
                    <div className="flex items-start justify-between mb-3">
                      <FileText className="w-8 h-8 text-indigo-400" />
                      <span className="text-xs px-2 py-1 bg-slate-800 rounded-full text-slate-400">{doc.type}</span>
                    </div>
                    <h4 className="text-white font-medium mb-1">{doc.title}</h4>
                    <p className="text-slate-500 text-sm">By {doc.author} • {doc.updated}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* PLACEHOLDER TABS */}
          {['investors', 'grants', 'partners', 'analytics', 'system', 'settings'].includes(activeTab) && (
            <div className="flex items-center justify-center h-96">
              <div className="text-center">
                <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
                  <RefreshCw className="w-8 h-8 text-slate-400" />
                </div>
                <h3 className="text-white font-bold text-lg capitalize">{activeTab} Section</h3>
                <p className="text-slate-400 mt-2">This section is being configured.</p>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default CommandDashboard;
