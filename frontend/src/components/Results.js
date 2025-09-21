import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { 
  Search, 
  Download, 
  Mail, 
  Phone, 
  Globe, 
  MapPin, 
  Star, 
  Filter,
  RefreshCw,
  CheckCircle,
  ExternalLink
} from "lucide-react";
import { mockScrapeResults } from "../data/mockScrapeResults";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Results = () => {
  const [results, setResults] = useState([]);
  const [searchData, setSearchData] = useState({});
  const [filteredResults, setFilteredResults] = useState([]);
  const [filterText, setFilterText] = useState("");
  const [enrichedEmails, setEnrichedEmails] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    const savedResults = localStorage.getItem('scrapeResults');
    const savedSearch = localStorage.getItem('lastSearch');
    
    if (savedResults && savedSearch) {
      const parsedResults = JSON.parse(savedResults);
      setResults(parsedResults);
      setFilteredResults(parsedResults);
      setSearchData(JSON.parse(savedSearch));
    } else {
      // Fallback zu Demo-Daten falls keine gespeicherte Suche vorhanden
      const demoResults = JSON.parse(localStorage.getItem('scrapeResults')) || mockScrapeResults;
      const demoSearch = { query: "restaurants", city: "München", state: "BY", zipCode: "80331", maxResults: 20 };
      
      setResults(demoResults);
      setFilteredResults(demoResults);
      setSearchData(demoSearch);
      
      // Demo-Daten in localStorage speichern für Konsistenz
      localStorage.setItem('scrapeResults', JSON.stringify(demoResults));
      localStorage.setItem('lastSearch', JSON.stringify(demoSearch));
    }
  }, [navigate]);

  useEffect(() => {
    if (filterText) {
      const filtered = results.filter(result => 
        result.businessName.toLowerCase().includes(filterText.toLowerCase()) ||
        result.businessType.toLowerCase().includes(filterText.toLowerCase()) ||
        result.address.toLowerCase().includes(filterText.toLowerCase())
      );
      setFilteredResults(filtered);
    } else {
      setFilteredResults(results);
    }
  }, [filterText, results]);

  const handleEnrichEmail = async (index, website) => {
    if (!website) return;
    
    const result = results[index];
    if (!result || !result.id) return;
    
    setEnrichedEmails(prev => ({ ...prev, [index]: 'loading' }));
    
    try {
      const response = await axios.post(`${API}/leads/enrich-email`, {
        leadId: result.id,
        website: website
      });
      
      if (response.data.success && response.data.email) {
        const enrichedEmail = response.data.email;
        setEnrichedEmails(prev => ({ ...prev, [index]: enrichedEmail }));
        
        // Ergebnis mit angereicherter E-Mail aktualisieren
        setResults(prev => prev.map((result, i) => 
          i === index ? { ...result, email: enrichedEmail } : result
        ));
      } else {
        setEnrichedEmails(prev => ({ ...prev, [index]: 'not_found' }));
      }
    } catch (error) {
      console.error('E-Mail-Anreicherungsfehler:', error);
      setEnrichedEmails(prev => ({ ...prev, [index]: 'error' }));
    }
  };

  const exportToCSV = () => {
    const headers = [
      'Firmenname',
      'Typ', 
      'Adresse',
      'Telefon',
      'Website',
      'E-Mail',
      'Bewertung',
      'Rezensionen',
      'Suchbegriff'
    ];
    
    const csvData = filteredResults.map(result => [
      result.businessName,
      result.businessType,
      result.address,
      result.phone || '',
      result.website || '',
      result.email || '',
      result.rating || '',
      result.reviewCount || '',
      searchData.query || ''
    ]);
    
    const csvContent = [headers, ...csvData]
      .map(row => row.map(field => `"${field}"`).join(','))
      .join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `leads_${searchData.query}_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    window.URL.revokeObjectURL(url);
  };

  if (!results.length) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Keine Ergebnisse gefunden</h2>
          <p className="text-gray-600 mb-4">Bitte führen Sie zuerst eine Suche durch</p>
          <Button onClick={() => navigate('/scraper')}>
            Zum Scraper gehen
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Search className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold text-gray-900">LeadMaps</span>
          </Link>
          <nav className="flex gap-4">
            <Button variant="outline" onClick={() => navigate('/scraper')}>
              Neue Suche
            </Button>
            <Button onClick={exportToCSV} className="bg-green-600 hover:bg-green-700">
              <Download className="w-4 h-4 mr-2" />
              CSV exportieren
            </Button>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Results Header */}
        <div className="mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Suchergebnisse
              </h1>
              <div className="flex flex-wrap items-center gap-2 text-sm text-gray-600">
                <Badge variant="secondary">
                  {searchData.query} in {searchData.city}, {searchData.state}
                </Badge>
                <span>•</span>
                <span>{filteredResults.length} von {results.length} Ergebnissen</span>
              </div>
            </div>
            <div className="flex gap-3">
              <div className="relative">
                <Filter className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input
                  placeholder="Ergebnisse filtern..."
                  value={filterText}
                  onChange={(e) => setFilterText(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
            </div>
          </div>

          {/* Summary Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <Card className="p-4">
              <div className="text-2xl font-bold text-blue-600">{results.length}</div>
              <div className="text-sm text-gray-600">Gesamt-Leads</div>
            </Card>
            <Card className="p-4">
              <div className="text-2xl font-bold text-green-600">
                {results.filter(r => r.phone).length}
              </div>
              <div className="text-sm text-gray-600">Mit Telefon</div>
            </Card>
            <Card className="p-4">
              <div className="text-2xl font-bold text-purple-600">
                {results.filter(r => r.email).length}
              </div>
              <div className="text-sm text-gray-600">Mit E-Mail</div>
            </Card>
            <Card className="p-4">
              <div className="text-2xl font-bold text-yellow-600">
                {results.filter(r => r.rating >= 4).length}
              </div>
              <div className="text-sm text-gray-600">4+ Sterne</div>
            </Card>
          </div>
        </div>

        <Tabs defaultValue="grid" className="w-full">
          <TabsList className="grid w-full grid-cols-2 max-w-md">
            <TabsTrigger value="grid">Rasteransicht</TabsTrigger>
            <TabsTrigger value="table">Tabellenansicht</TabsTrigger>
          </TabsList>
          
          <TabsContent value="grid" className="space-y-6">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredResults.map((result, index) => (
                <Card key={index} className="hover:shadow-lg transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg mb-1">{result.businessName}</CardTitle>
                        <CardDescription className="flex items-center gap-1">
                          <Badge variant="secondary" className="text-xs">
                            {result.businessType}
                          </Badge>
                        </CardDescription>
                      </div>
                      {result.rating && (
                        <div className="flex items-center gap-1 text-sm">
                          <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                          <span className="font-medium">{result.rating}</span>
                          <span className="text-gray-500">({result.reviewCount})</span>
                        </div>
                      )}
                    </div>
                  </CardHeader>
                  
                  <CardContent className="space-y-3">
                    <div className="flex items-start gap-2 text-sm text-gray-600">
                      <MapPin className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <span className="break-words">{result.address}</span>
                    </div>
                    
                    {result.phone && (
                      <div className="flex items-center gap-2 text-sm">
                        <Phone className="w-4 h-4 text-green-600" />
                        <a 
                          href={`tel:${result.phone}`}
                          className="text-green-600 hover:underline"
                        >
                          {result.phone}
                        </a>
                      </div>
                    )}
                    
                    {result.website && (
                      <div className="flex items-center gap-2 text-sm">
                        <Globe className="w-4 h-4 text-blue-600" />
                        <a 
                          href={result.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline flex items-center gap-1"
                        >
                          Website besuchen
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    )}
                    
                    <div className="flex items-center gap-2 text-sm">
                      <Mail className="w-4 h-4 text-purple-600" />
                      {result.email ? (
                        <a 
                          href={`mailto:${result.email}`}
                          className="text-purple-600 hover:underline"
                        >
                          {result.email}
                        </a>
                      ) : (
                        <div className="flex items-center gap-2">
                          {enrichedEmails[index] === 'loading' ? (
                            <div className="flex items-center gap-2">
                              <RefreshCw className="w-3 h-3 animate-spin" />
                              <span className="text-gray-500">E-Mail wird gesucht...</span>
                            </div>
                          ) : enrichedEmails[index] && enrichedEmails[index] !== 'loading' && enrichedEmails[index] !== 'not_found' && enrichedEmails[index] !== 'error' ? (
                            <div className="flex items-center gap-2">
                              <CheckCircle className="w-3 h-3 text-green-500" />
                              <a 
                                href={`mailto:${enrichedEmails[index]}`}
                                className="text-purple-600 hover:underline"
                              >
                                {enrichedEmails[index]}
                              </a>
                            </div>
                          ) : (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleEnrichEmail(index, result.website)}
                              disabled={!result.website || enrichedEmails[index] === 'not_found'}
                              className="text-xs"
                            >
                              {enrichedEmails[index] === 'not_found' ? 'Nicht gefunden' : 'E-Mail finden'}
                            </Button>
                          )}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
          
          <TabsContent value="table" className="space-y-6">
            <div className="bg-white rounded-lg border overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="text-left p-4 font-medium text-gray-900">Business</th>
                      <th className="text-left p-4 font-medium text-gray-900">Contact</th>
                      <th className="text-left p-4 font-medium text-gray-900">Location</th>
                      <th className="text-left p-4 font-medium text-gray-900">Rating</th>
                      <th className="text-left p-4 font-medium text-gray-900">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredResults.map((result, index) => (
                      <tr key={index} className="border-b hover:bg-gray-50">
                        <td className="p-4">
                          <div>
                            <div className="font-medium text-gray-900">{result.businessName}</div>
                            <div className="text-sm text-gray-500">{result.businessType}</div>
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="space-y-1">
                            {result.phone && (
                              <div className="flex items-center gap-1 text-sm">
                                <Phone className="w-3 h-3" />
                                {result.phone}
                              </div>
                            )}
                            {result.email && (
                              <div className="flex items-center gap-1 text-sm">
                                <Mail className="w-3 h-3" />
                                {result.email}
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="text-sm text-gray-600 max-w-xs break-words">
                            {result.address}
                          </div>
                        </td>
                        <td className="p-4">
                          {result.rating && (
                            <div className="flex items-center gap-1">
                              <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                              <span className="text-sm font-medium">{result.rating}</span>
                              <span className="text-xs text-gray-500">({result.reviewCount})</span>
                            </div>
                          )}
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            {result.website && (
                              <Button size="sm" variant="outline" asChild>
                                <a href={result.website} target="_blank" rel="noopener noreferrer">
                                  <ExternalLink className="w-3 h-3" />
                                </a>
                              </Button>
                            )}
                            {!result.email && result.website && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleEnrichEmail(index, result.website)}
                                disabled={enrichedEmails[index] === 'loading'}
                              >
                                {enrichedEmails[index] === 'loading' ? (
                                  <RefreshCw className="w-3 h-3 animate-spin" />
                                ) : (
                                  <Mail className="w-3 h-3" />
                                )}
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Results;