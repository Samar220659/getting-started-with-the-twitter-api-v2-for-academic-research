import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { 
  Activity, 
  CheckCircle, 
  AlertTriangle, 
  Play, 
  Pause, 
  RotateCcw,
  Monitor,
  Database,
  Zap,
  Clock,
  TrendingUp,
  Users,
  Search
} from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AutomationDashboard = () => {
  const [overview, setOverview] = useState(null);
  const [workflows, setWorkflows] = useState([]);
  const [systemHealth, setSystemHealth] = useState(null);
  const [recentTasks, setRecentTasks] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Alle 30 Sekunden
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [overviewRes, workflowsRes, healthRes, tasksRes, statsRes] = await Promise.all([
        axios.get(`${API}/automation/dashboard/overview`),
        axios.get(`${API}/automation/workflows/status`),
        axios.get(`${API}/automation/system/health`),
        axios.get(`${API}/automation/tasks/recent?limit=20`),
        axios.get(`${API}/automation/statistics/summary`)
      ]);

      setOverview(overviewRes.data);
      setWorkflows(workflowsRes.data);
      setSystemHealth(healthRes.data);
      setRecentTasks(tasksRes.data.tasks);
      setStatistics(statsRes.data);
    } catch (error) {
      console.error('Fehler beim Laden der Dashboard-Daten:', error);
    } finally {
      setLoading(false);
    }
  };

  const triggerWorkflow = async (workflowName) => {
    try {
      await axios.post(`${API}/automation/workflows/${workflowName}/trigger`);
      alert(`Workflow "${workflowName}" wurde manuell gestartet!`);
      fetchDashboardData(); // Dashboard aktualisieren
    } catch (error) {
      console.error('Fehler beim Starten des Workflows:', error);
      alert('Fehler beim Starten des Workflows');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'running': return 'text-blue-600';
      case 'failed': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      case 'running': return <Activity className="w-4 h-4 animate-pulse" />;
      case 'failed': return <AlertTriangle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const getWorkflowDisplayName = (workflowName) => {
    const names = {
      'google_maps_scraper': 'Google Maps Lead-Scraper',
      'linkedin_extractor': 'LinkedIn Profil-Extraktor',
      'ecommerce_intelligence': 'E-Commerce Intelligence',
      'social_media_harvester': 'Social Media Harvester',
      'real_estate_analyzer': 'Immobilienmarkt-Analyzer',
      'job_market_intelligence': 'Jobmarkt-Intelligence',
      'restaurant_analyzer': 'Restaurant-Analyzer',
      'finance_data_collector': 'Finanzdaten-Collector',
      'event_scout': 'Event-Scout',
      'vehicle_market_intel': 'Fahrzeugmarkt-Intelligence',
      'seo_opportunity_finder': 'SEO-Opportunity-Finder'
    };
    return names[workflowName] || workflowName;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Activity className="w-12 h-12 text-blue-600 mx-auto mb-4 animate-spin" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Dashboard wird geladen...</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center">
              <Monitor className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Automation Manager</h1>
              <p className="text-sm text-gray-500">11 Workflows • 24/7 Automatisierung</p>
            </div>
          </div>
          <nav className="flex gap-4">
            <Button variant="outline" asChild>
              <Link to="/dashboard">LeadMaps Dashboard</Link>
            </Button>
            <Button onClick={fetchDashboardData} variant="outline">
              <RotateCcw className="w-4 h-4 mr-2" />
              Aktualisieren
            </Button>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Übersichts-Statistiken */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Aktive Workflows</CardTitle>
              <Zap className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{overview?.active_workflows || 0}</div>
              <p className="text-xs text-muted-foreground">
                von {overview?.total_workflows || 11} verfügbaren
              </p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Tasks (24h)</CardTitle>
              <Activity className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{overview?.total_tasks_24h || 0}</div>
              <p className="text-xs text-muted-foreground">
                <span className="text-green-600">{overview?.successful_tasks_24h || 0} erfolgreich</span>
              </p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Generierte Leads</CardTitle>
              <Users className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{overview?.total_results_24h || 0}</div>
              <p className="text-xs text-muted-foreground">
                Letzte 24 Stunden
              </p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">System-Status</CardTitle>
              <Monitor className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                <Badge 
                  variant={systemHealth?.overall_status === 'healthy' ? 'default' : 'destructive'}
                  className={systemHealth?.overall_status === 'healthy' ? 'bg-green-600' : ''}
                >
                  {systemHealth?.overall_status === 'healthy' ? 'Gesund' : 'Warnung'}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground">
                Alle Services aktiv
              </p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="workflows" className="w-full">
          <TabsList className="grid w-full grid-cols-4 max-w-2xl">
            <TabsTrigger value="workflows">Workflows</TabsTrigger>
            <TabsTrigger value="tasks">Aktuelle Tasks</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="system">System</TabsTrigger>
          </TabsList>

          <TabsContent value="workflows" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Workflow-Status & Steuerung</CardTitle>
                <CardDescription>
                  Übersicht aller automatisierten Workflows mit manueller Trigger-Möglichkeit
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {workflows.map((workflow) => (
                    <Card key={workflow.workflow_name} className="hover:shadow-md transition-shadow">
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-base">
                            {getWorkflowDisplayName(workflow.workflow_name)}
                          </CardTitle>
                          <div className={`flex items-center gap-1 ${getStatusColor(workflow.status)}`}>
                            {getStatusIcon(workflow.status)}
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Status:</span>
                            <Badge variant={workflow.status === 'completed' ? 'default' : 'secondary'}>
                              {workflow.status === 'completed' ? 'Abgeschlossen' :
                               workflow.status === 'running' ? 'Läuft' :
                               workflow.status === 'failed' ? 'Fehlgeschlagen' : 'Bereit'}
                            </Badge>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Erfolgsrate:</span>
                            <span className="font-medium">
                              {(workflow.success_rate * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Ausführungen:</span>
                            <span className="font-medium">{workflow.total_runs}</span>
                          </div>
                        </div>
                        
                        <Button 
                          size="sm" 
                          className="w-full" 
                          onClick={() => triggerWorkflow(workflow.workflow_name)}
                          disabled={workflow.status === 'running'}
                        >
                          <Play className="w-3 h-3 mr-1" />
                          {workflow.status === 'running' ? 'Läuft bereits' : 'Manuell starten'}
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="tasks" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Aktuelle Tasks</CardTitle>
                <CardDescription>
                  Letzte 20 ausgeführte Automatisierungs-Tasks
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {recentTasks.map((task) => (
                    <div key={task.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className={`${getStatusColor(task.status)}`}>
                          {getStatusIcon(task.status)}
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">
                            {getWorkflowDisplayName(task.workflow_type)}
                          </h4>
                          <p className="text-sm text-gray-500">
                            {new Date(task.started_at).toLocaleString('de-DE')}
                            {task.results_count > 0 && ` • ${task.results_count} Ergebnisse`}
                          </p>
                        </div>
                      </div>
                      <Badge variant={task.status === 'completed' ? 'default' : 'secondary'}>
                        {task.status === 'completed' ? 'Erfolgreich' :
                         task.status === 'running' ? 'Läuft' :
                         task.status === 'failed' ? 'Fehlgeschlagen' : task.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="performance" className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Performance-Übersicht</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {statistics?.periods && Object.entries(statistics.periods).map(([period, stats]) => (
                    <div key={period} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">
                          {period === 'last_hour' ? 'Letzte Stunde' :
                           period === 'last_24h' ? 'Letzte 24h' :
                           period === 'last_week' ? 'Letzte Woche' : 'Letzter Monat'}
                        </span>
                        <Badge variant="outline">
                          {(stats.success_rate * 100).toFixed(1)}% Erfolg
                        </Badge>
                      </div>
                      <div className="grid grid-cols-3 gap-2 text-xs">
                        <div className="text-center p-2 bg-green-50 rounded">
                          <div className="font-semibold text-green-600">{stats.successful_tasks}</div>
                          <div className="text-green-600">Erfolgreich</div>
                        </div>
                        <div className="text-center p-2 bg-red-50 rounded">
                          <div className="font-semibold text-red-600">{stats.failed_tasks}</div>
                          <div className="text-red-600">Fehlgeschlagen</div>
                        </div>
                        <div className="text-center p-2 bg-blue-50 rounded">
                          <div className="font-semibold text-blue-600">{stats.total_results}</div>
                          <div className="text-blue-600">Ergebnisse</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Workflow-Verteilung</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {overview?.workflow_statistics && Object.entries(overview.workflow_statistics)
                      .sort(([,a], [,b]) => b.total_runs - a.total_runs)
                      .slice(0, 5)
                      .map(([workflowName, stats]) => (
                      <div key={workflowName} className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="text-sm font-medium">
                            {getWorkflowDisplayName(workflowName)}
                          </div>
                          <div className="text-xs text-gray-500">
                            {stats.total_runs} Ausführungen
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium">
                            {(stats.success_rate * 100).toFixed(1)}%
                          </div>
                          <div className="text-xs text-gray-500">
                            {stats.total_results} Ergebnisse
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="system" className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>System-Health</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {systemHealth?.services && Object.entries(systemHealth.services).map(([service, status]) => (
                    <div key={service} className="flex items-center justify-between p-2 border rounded">
                      <span className="font-medium">{service}</span>
                      <Badge variant={status.status === 'healthy' ? 'default' : 'destructive'}>
                        {status.status === 'healthy' ? 'Gesund' : 'Fehler'}
                      </Badge>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>System-Ressourcen</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {systemHealth?.system_resources && (
                    <>
                      <div className="flex justify-between items-center">
                        <span>CPU-Auslastung</span>
                        <span className="font-medium">{systemHealth.system_resources.cpu_percent}%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span>Speicher-Auslastung</span>
                        <span className="font-medium">{systemHealth.system_resources.memory_percent}%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span>Festplatte</span>
                        <span className="font-medium">{systemHealth.system_resources.disk_percent}%</span>
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>

        {/* Schnellaktionen */}
        <div className="mt-8">
          <Card className="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
            <CardHeader>
              <CardTitle className="text-purple-800">🚀 Autonome Automatisierung aktiv</CardTitle>
              <CardDescription className="text-purple-600">
                Alle 11 Workflows laufen vollautomatisch 24/7 im Hintergrund und generieren kontinuierlich wertvolle Leads und Daten
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col sm:flex-row gap-3">
                <Button onClick={() => window.open('/api/automation/dashboard/overview', '_blank')} className="bg-purple-600 hover:bg-purple-700">
                  <Database className="w-4 h-4 mr-2" />
                  API-Dokumentation
                </Button>
                <Button variant="outline" onClick={() => navigate('/results')}>
                  <TrendingUp className="w-4 h-4 mr-2" />
                  Generierte Leads anzeigen
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default AutomationDashboard;