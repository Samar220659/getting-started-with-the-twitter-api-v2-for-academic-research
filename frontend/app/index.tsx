import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  RefreshControl,
  Modal,
  Switch,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Workflow {
  id: string;
  name: string;
  description: string;
  type: string;
  status: string;
  total_revenue: number;
  leads_generated: number;
  content_created: number;
  created_at: string;
}

interface Stats {
  total_workflows: number;
  active_workflows: number;
  total_leads: number;
  total_revenue: number;
  content_created_today: number;
  posts_scheduled: number;
}

interface Lead {
  id: string;
  email: string;
  company?: string;
  industry?: string;
  score: number;
  source: string;
  status: string;
  created_at: string;
}

interface Content {
  id: string;
  title: string;
  content_type: string;
  content: string;
  published: boolean;
  created_at: string;
}

export default function Index() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [content, setContent] = useState<Content[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  
  // Modal states
  const [showWorkflowModal, setShowWorkflowModal] = useState(false);
  const [showLeadModal, setShowLeadModal] = useState(false);
  const [showContentModal, setShowContentModal] = useState(false);
  
  // Form states
  const [workflowForm, setWorkflowForm] = useState({
    name: '',
    description: '',
    type: 'lead_gen'
  });
  
  const [leadForm, setLeadForm] = useState({
    email: '',
    company: '',
    industry: '',
    source: 'website',
    workflow_id: ''
  });
  
  const [contentForm, setContentForm] = useState({
    content_type: 'video_script',
    target_audience: '',
    keywords: '',
    workflow_id: ''
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch stats
      const statsResponse = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/stats`);
      const statsData = await statsResponse.json();
      setStats(statsData);
      
      // Fetch workflows
      const workflowsResponse = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/workflows`);
      const workflowsData = await workflowsResponse.json();
      setWorkflows(workflowsData);
      
      // Fetch leads
      const leadsResponse = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/leads`);
      const leadsData = await leadsResponse.json();
      setLeads(leadsData.slice(0, 10)); // Latest 10 leads
      
      // Fetch content
      const contentResponse = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/content`);
      const contentData = await contentResponse.json();
      setContent(contentData.slice(0, 10)); // Latest 10 content
      
    } catch (error) {
      Alert.alert('Fehler', 'Daten konnten nicht geladen werden');
      console.error('Fetch error:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  const createWorkflow = async () => {
    if (!workflowForm.name || !workflowForm.description) {
      Alert.alert('Fehler', 'Bitte alle Felder ausfüllen');
      return;
    }

    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/workflows`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(workflowForm),
      });

      if (response.ok) {
        Alert.alert('Erfolg', 'Workflow wurde erstellt');
        setShowWorkflowModal(false);
        setWorkflowForm({ name: '', description: '', type: 'lead_gen' });
        fetchData();
      } else {
        Alert.alert('Fehler', 'Workflow konnte nicht erstellt werden');
      }
    } catch (error) {
      Alert.alert('Fehler', 'Netzwerkfehler');
    }
  };

  const createLead = async () => {
    if (!leadForm.email || !leadForm.workflow_id) {
      Alert.alert('Fehler', 'E-Mail und Workflow sind erforderlich');
      return;
    }

    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/leads`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...leadForm,
          pain_points: []
        }),
      });

      if (response.ok) {
        Alert.alert('Erfolg', 'Lead wurde erstellt');
        setShowLeadModal(false);
        setLeadForm({ email: '', company: '', industry: '', source: 'website', workflow_id: '' });
        fetchData();
      } else {
        Alert.alert('Fehler', 'Lead konnte nicht erstellt werden');
      }
    } catch (error) {
      Alert.alert('Fehler', 'Netzwerkfehler');
    }
  };

  const generateContent = async () => {
    if (!contentForm.target_audience || !contentForm.workflow_id) {
      Alert.alert('Fehler', 'Zielgruppe und Workflow sind erforderlich');
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/content/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...contentForm,
          keywords: contentForm.keywords.split(',').map(k => k.trim()).filter(k => k)
        }),
      });

      if (response.ok) {
        Alert.alert('Erfolg', 'Content wurde generiert');
        setShowContentModal(false);
        setContentForm({ content_type: 'video_script', target_audience: '', keywords: '', workflow_id: '' });
        fetchData();
      } else {
        Alert.alert('Fehler', 'Content konnte nicht generiert werden');
      }
    } catch (error) {
      Alert.alert('Fehler', 'Netzwerkfehler');
    } finally {
      setLoading(false);
    }
  };

  const toggleWorkflowStatus = async (workflowId: string, currentStatus: string) => {
    const newStatus = currentStatus === 'active' ? 'paused' : 'active';
    
    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/workflows/${workflowId}/status?status=${newStatus}`, {
        method: 'PUT',
      });

      if (response.ok) {
        fetchData();
      } else {
        Alert.alert('Fehler', 'Status konnte nicht geändert werden');
      }
    } catch (error) {
      Alert.alert('Fehler', 'Netzwerkfehler');
    }
  };

  const triggerAutomation = async (leadId: string) => {
    try {
      setLoading(true);
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/automation/lead-to-content/${leadId}`, {
        method: 'POST',
      });

      if (response.ok) {
        Alert.alert('Erfolg', 'Automatisierung wurde gestartet');
        fetchData();
      } else {
        Alert.alert('Fehler', 'Automatisierung konnte nicht gestartet werden');
      }
    } catch (error) {
      Alert.alert('Fehler', 'Netzwerkfehler');
    } finally {
      setLoading(false);
    }
  };

  const renderDashboard = () => (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <View style={styles.header}>
        <Text style={styles.headerTitle}>ZZ-LOBBY-BOOST</Text>
        <Text style={styles.headerSubtitle}>Autonome Einkommensgenerierung</Text>
      </View>

      {stats && (
        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Ionicons name="trending-up" size={24} color="#4CAF50" />
            <Text style={styles.statValue}>€{stats.total_revenue.toFixed(2)}</Text>
            <Text style={styles.statLabel}>Gesamtumsatz</Text>
          </View>
          <View style={styles.statCard}>
            <Ionicons name="people" size={24} color="#2196F3" />
            <Text style={styles.statValue}>{stats.total_leads}</Text>
            <Text style={styles.statLabel}>Leads</Text>
          </View>
          <View style={styles.statCard}>
            <Ionicons name="play" size={24} color="#FF9800" />
            <Text style={styles.statValue}>{stats.active_workflows}</Text>
            <Text style={styles.statLabel}>Aktive Workflows</Text>
          </View>
          <View style={styles.statCard}>
            <Ionicons name="create" size={24} color="#9C27B0" />
            <Text style={styles.statValue}>{stats.content_created_today}</Text>
            <Text style={styles.statLabel}>Content heute</Text>
          </View>
        </View>
      )}

      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Workflows</Text>
          <TouchableOpacity
            style={styles.addButton}
            onPress={() => setShowWorkflowModal(true)}
          >
            <Ionicons name="add" size={20} color="#fff" />
          </TouchableOpacity>
        </View>
        
        {workflows.map((workflow) => (
          <View key={workflow.id} style={styles.workflowCard}>
            <View style={styles.workflowHeader}>
              <View>
                <Text style={styles.workflowName}>{workflow.name}</Text>
                <Text style={styles.workflowType}>{workflow.type}</Text>
              </View>
              <Switch
                value={workflow.status === 'active'}
                onValueChange={() => toggleWorkflowStatus(workflow.id, workflow.status)}
                trackColor={{ false: '#767577', true: '#4CAF50' }}
              />
            </View>
            <Text style={styles.workflowDescription}>{workflow.description}</Text>
            <View style={styles.workflowStats}>
              <Text style={styles.workflowStat}>€{workflow.total_revenue.toFixed(2)} Umsatz</Text>
              <Text style={styles.workflowStat}>{workflow.leads_generated} Leads</Text>
              <Text style={styles.workflowStat}>{workflow.content_created} Content</Text>
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
  );

  const renderLeads = () => (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Leads</Text>
          <TouchableOpacity
            style={styles.addButton}
            onPress={() => setShowLeadModal(true)}
          >
            <Ionicons name="add" size={20} color="#fff" />
          </TouchableOpacity>
        </View>

        {leads.map((lead) => (
          <View key={lead.id} style={styles.leadCard}>
            <View style={styles.leadHeader}>
              <View>
                <Text style={styles.leadEmail}>{lead.email}</Text>
                <Text style={styles.leadCompany}>{lead.company || 'Kein Unternehmen'}</Text>
              </View>
              <View style={styles.leadScore}>
                <Text style={styles.scoreText}>{lead.score}/10</Text>
              </View>
            </View>
            <View style={styles.leadMeta}>
              <Text style={styles.leadSource}>Quelle: {lead.source}</Text>
              <Text style={styles.leadStatus}>Status: {lead.status}</Text>
            </View>
            <TouchableOpacity
              style={styles.automationButton}
              onPress={() => triggerAutomation(lead.id)}
            >
              <Ionicons name="flash" size={16} color="#fff" />
              <Text style={styles.automationButtonText}>Automatisierung starten</Text>
            </TouchableOpacity>
          </View>
        ))}
      </View>
    </ScrollView>
  );

  const renderContent = () => (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Content</Text>
          <TouchableOpacity
            style={styles.addButton}
            onPress={() => setShowContentModal(true)}
          >
            <Ionicons name="add" size={20} color="#fff" />
          </TouchableOpacity>
        </View>

        {content.map((item) => (
          <View key={item.id} style={styles.contentCard}>
            <View style={styles.contentHeader}>
              <Text style={styles.contentTitle}>{item.title}</Text>
              <View style={styles.contentType}>
                <Text style={styles.contentTypeText}>{item.content_type}</Text>
              </View>
            </View>
            <Text style={styles.contentPreview} numberOfLines={3}>
              {item.content}
            </Text>
            <View style={styles.contentMeta}>
              <Text style={styles.contentDate}>
                {new Date(item.created_at).toLocaleDateString('de-DE')}
              </Text>
              <View style={[styles.contentStatus, { backgroundColor: item.published ? '#4CAF50' : '#FF9800' }]}>
                <Text style={styles.contentStatusText}>
                  {item.published ? 'Veröffentlicht' : 'Entwurf'}
                </Text>
              </View>
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
  );

  const renderWorkflowModal = () => (
    <Modal visible={showWorkflowModal} animationType="slide" transparent>
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Neuer Workflow</Text>
            <TouchableOpacity onPress={() => setShowWorkflowModal(false)}>
              <Ionicons name="close" size={24} color="#333" />
            </TouchableOpacity>
          </View>
          
          <TextInput
            style={styles.input}
            placeholder="Workflow Name"
            value={workflowForm.name}
            onChangeText={(text) => setWorkflowForm({ ...workflowForm, name: text })}
          />
          
          <TextInput
            style={[styles.input, styles.textArea]}
            placeholder="Beschreibung"
            value={workflowForm.description}
            onChangeText={(text) => setWorkflowForm({ ...workflowForm, description: text })}
            multiline
            numberOfLines={3}
          />
          
          <View style={styles.pickerContainer}>
            <Text style={styles.pickerLabel}>Typ:</Text>
            <View style={styles.pickerButtons}>
              {['lead_gen', 'content_creation', 'social_media', 'affiliate'].map((type) => (
                <TouchableOpacity
                  key={type}
                  style={[
                    styles.pickerButton,
                    workflowForm.type === type && styles.pickerButtonActive
                  ]}
                  onPress={() => setWorkflowForm({ ...workflowForm, type })}
                >
                  <Text style={[
                    styles.pickerButtonText,
                    workflowForm.type === type && styles.pickerButtonTextActive
                  ]}>
                    {type.replace('_', ' ')}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
          
          <TouchableOpacity style={styles.submitButton} onPress={createWorkflow}>
            <Text style={styles.submitButtonText}>Erstellen</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );

  const renderLeadModal = () => (
    <Modal visible={showLeadModal} animationType="slide" transparent>
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Neuer Lead</Text>
            <TouchableOpacity onPress={() => setShowLeadModal(false)}>
              <Ionicons name="close" size={24} color="#333" />
            </TouchableOpacity>
          </View>
          
          <TextInput
            style={styles.input}
            placeholder="E-Mail"
            value={leadForm.email}
            onChangeText={(text) => setLeadForm({ ...leadForm, email: text })}
            keyboardType="email-address"
          />
          
          <TextInput
            style={styles.input}
            placeholder="Unternehmen"
            value={leadForm.company}
            onChangeText={(text) => setLeadForm({ ...leadForm, company: text })}
          />
          
          <TextInput
            style={styles.input}
            placeholder="Branche"
            value={leadForm.industry}
            onChangeText={(text) => setLeadForm({ ...leadForm, industry: text })}
          />
          
          <View style={styles.pickerContainer}>
            <Text style={styles.pickerLabel}>Workflow:</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {workflows.map((workflow) => (
                <TouchableOpacity
                  key={workflow.id}
                  style={[
                    styles.pickerButton,
                    leadForm.workflow_id === workflow.id && styles.pickerButtonActive
                  ]}
                  onPress={() => setLeadForm({ ...leadForm, workflow_id: workflow.id })}
                >
                  <Text style={[
                    styles.pickerButtonText,
                    leadForm.workflow_id === workflow.id && styles.pickerButtonTextActive
                  ]}>
                    {workflow.name}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
          
          <TouchableOpacity style={styles.submitButton} onPress={createLead}>
            <Text style={styles.submitButtonText}>Erstellen</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );

  const renderContentModal = () => (
    <Modal visible={showContentModal} animationType="slide" transparent>
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Content generieren</Text>
            <TouchableOpacity onPress={() => setShowContentModal(false)}>
              <Ionicons name="close" size={24} color="#333" />
            </TouchableOpacity>
          </View>
          
          <View style={styles.pickerContainer}>
            <Text style={styles.pickerLabel}>Content-Typ:</Text>
            <View style={styles.pickerButtons}>
              {['video_script', 'social_post', 'email', 'blog'].map((type) => (
                <TouchableOpacity
                  key={type}
                  style={[
                    styles.pickerButton,
                    contentForm.content_type === type && styles.pickerButtonActive
                  ]}
                  onPress={() => setContentForm({ ...contentForm, content_type: type })}
                >
                  <Text style={[
                    styles.pickerButtonText,
                    contentForm.content_type === type && styles.pickerButtonTextActive
                  ]}>
                    {type.replace('_', ' ')}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
          
          <TextInput
            style={styles.input}
            placeholder="Zielgruppe"
            value={contentForm.target_audience}
            onChangeText={(text) => setContentForm({ ...contentForm, target_audience: text })}
          />
          
          <TextInput
            style={styles.input}
            placeholder="Keywords (kommagetrennt)"
            value={contentForm.keywords}
            onChangeText={(text) => setContentForm({ ...contentForm, keywords: text })}
          />
          
          <View style={styles.pickerContainer}>
            <Text style={styles.pickerLabel}>Workflow:</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {workflows.map((workflow) => (
                <TouchableOpacity
                  key={workflow.id}
                  style={[
                    styles.pickerButton,
                    contentForm.workflow_id === workflow.id && styles.pickerButtonActive
                  ]}
                  onPress={() => setContentForm({ ...contentForm, workflow_id: workflow.id })}
                >
                  <Text style={[
                    styles.pickerButtonText,
                    contentForm.workflow_id === workflow.id && styles.pickerButtonTextActive
                  ]}>
                    {workflow.name}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
          
          <TouchableOpacity style={styles.submitButton} onPress={generateContent}>
            <Text style={styles.submitButtonText}>Generieren</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return renderDashboard();
      case 'leads':
        return renderLeads();
      case 'content':
        return renderContent();
      default:
        return renderDashboard();
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#4CAF50" />
          <Text style={styles.loadingText}>Wird verarbeitet...</Text>
        </View>
      )}
      
      {renderTabContent()}
      
      <View style={styles.tabBar}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'dashboard' && styles.activeTab]}
          onPress={() => setActiveTab('dashboard')}
        >
          <Ionicons 
            name="analytics" 
            size={24} 
            color={activeTab === 'dashboard' ? '#4CAF50' : '#999'} 
          />
          <Text style={[styles.tabText, activeTab === 'dashboard' && styles.activeTabText]}>
            Dashboard
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.tab, activeTab === 'leads' && styles.activeTab]}
          onPress={() => setActiveTab('leads')}
        >
          <Ionicons 
            name="people" 
            size={24} 
            color={activeTab === 'leads' ? '#4CAF50' : '#999'} 
          />
          <Text style={[styles.tabText, activeTab === 'leads' && styles.activeTabText]}>
            Leads
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.tab, activeTab === 'content' && styles.activeTab]}
          onPress={() => setActiveTab('content')}
        >
          <Ionicons 
            name="create" 
            size={24} 
            color={activeTab === 'content' ? '#4CAF50' : '#999'} 
          />
          <Text style={[styles.tabText, activeTab === 'content' && styles.activeTabText]}>
            Content
          </Text>
        </TouchableOpacity>
      </View>

      {renderWorkflowModal()}
      {renderLeadModal()}
      {renderContentModal()}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#1a1a1a',
    padding: 20,
    paddingTop: 40,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4CAF50',
    textAlign: 'center',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#ccc',
    textAlign: 'center',
    marginTop: 4,
  },
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 16,
    gap: 12,
  },
  statCard: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  section: {
    margin: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  addButton: {
    backgroundColor: '#4CAF50',
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  workflowCard: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  workflowHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  workflowName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  workflowType: {
    fontSize: 12,
    color: '#666',
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    marginTop: 4,
  },
  workflowDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
  },
  workflowStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  workflowStat: {
    fontSize: 12,
    color: '#4CAF50',
    fontWeight: '500',
  },
  leadCard: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  leadHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  leadEmail: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  leadCompany: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  leadScore: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  scoreText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  leadMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  leadSource: {
    fontSize: 12,
    color: '#666',
  },
  leadStatus: {
    fontSize: 12,
    color: '#666',
  },
  automationButton: {
    flexDirection: 'row',
    backgroundColor: '#FF9800',
    padding: 8,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  automationButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
    marginLeft: 4,
  },
  contentCard: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  contentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  contentTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  contentType: {
    backgroundColor: '#9C27B0',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
  },
  contentTypeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  contentPreview: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
    lineHeight: 20,
  },
  contentMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  contentDate: {
    fontSize: 12,
    color: '#666',
  },
  contentStatus: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
  },
  contentStatusText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
  },
  activeTab: {
    borderTopWidth: 2,
    borderTopColor: '#4CAF50',
  },
  tabText: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  activeTabText: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#fff',
    width: '90%',
    maxHeight: '80%',
    borderRadius: 12,
    padding: 20,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
    fontSize: 16,
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  pickerContainer: {
    marginBottom: 16,
  },
  pickerLabel: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  pickerButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  pickerButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#ddd',
    backgroundColor: '#f9f9f9',
  },
  pickerButtonActive: {
    backgroundColor: '#4CAF50',
    borderColor: '#4CAF50',
  },
  pickerButtonText: {
    fontSize: 12,
    color: '#333',
  },
  pickerButtonTextActive: {
    color: '#fff',
    fontWeight: 'bold',
  },
  submitButton: {
    backgroundColor: '#4CAF50',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  loadingText: {
    color: '#fff',
    marginTop: 12,
    fontSize: 16,
  },
});