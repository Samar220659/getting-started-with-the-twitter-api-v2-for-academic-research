import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Badge } from "./ui/badge";
import { Search, MapPin, Loader2, ArrowRight, Zap, Download } from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LeadScraper = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [searchData, setSearchData] = useState({
    query: "",
    city: "",
    state: "",
    zipCode: "",
    maxResults: 20
  });
  const navigate = useNavigate();

  const handleInputChange = (field, value) => {
    setSearchData(prev => ({ ...prev, [field]: value }));
  };

  const handleScrape = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      // Make API call to backend
      const response = await axios.post(`${API}/leads/scrape`, searchData);
      
      if (response.data && response.data.results) {
        // Store search data and results
        localStorage.setItem('lastSearch', JSON.stringify(searchData));
        localStorage.setItem('scrapeResults', JSON.stringify(response.data.results));
        
        // Navigate to results
        navigate('/results');
      } else {
        alert('Keine Ergebnisse gefunden. Bitte versuchen Sie eine andere Suche.');
      }
    } catch (error) {
      console.error('Scraping-Fehler:', error);
      alert('Suche fehlgeschlagen. Bitte versuchen Sie es erneut oder kontaktieren Sie den Support.');
    } finally {
      setIsLoading(false);
    }
  };

  const exampleSearches = [
    { query: "restaurants", city: "München", state: "BY" },
    { query: "klempner", city: "Berlin", state: "BE" },
    { query: "friseursalons", city: "Hamburg", state: "HH" },
    { query: "fitnessstudios", city: "Köln", state: "NW" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
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
            <Button variant="outline" asChild>
              <Link to="/dashboard">Ergebnisse anzeigen</Link>
            </Button>
          </nav>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <Badge className="mb-4 bg-blue-100 text-blue-700 border-blue-200">
            <Zap className="w-4 h-4 mr-1" />
            Export-Button-Theorie in Aktion
          </Badge>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Google Maps Lead Scraper
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Anstatt Daten manuell von Google Maps zu kopieren, lassen Sie unsere Automatisierung die Arbeit machen. 
            Erhalten Sie Unternehmensdetails, Kontaktinformationen und Bewertungen in Sekunden.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Form */}
          <div className="lg:col-span-2">
            <Card className="shadow-lg border-0">
              <CardHeader className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-t-lg">
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="w-5 h-5" />
                  Lead-Scraping-Parameter
                </CardTitle>
                <CardDescription className="text-blue-100">
                  Konfigurieren Sie Ihre Suche, um genau die Unternehmen zu finden, die Sie benötigen
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <form onSubmit={handleScrape} className="space-y-6">
                  <div className="space-y-2">
                    <Label htmlFor="query" className="text-sm font-medium">
                      Wonach suchen Sie? *
                    </Label>
                    <Input
                      id="query"
                      name="query"
                      placeholder="z.B. restaurants, klempner, fitnessstudios, friseursalons"
                      value={searchData.query}
                      onChange={(e) => handleInputChange('query', e.target.value)}
                      required
                      className="text-lg"
                      autoComplete="off"
                    />
                    <p className="text-sm text-gray-500">
                      Seien Sie spezifisch für bessere Ergebnisse (z.B. "italienische Restaurants" statt "Restaurants")
                    </p>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="city">Stadt *</Label>
                      <Input
                        id="city"
                        name="city"
                        placeholder="München"
                        value={searchData.city}
                        onChange={(e) => handleInputChange('city', e.target.value)}
                        required
                        autoComplete="off"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="state">Bundesland *</Label>
                      <Input
                        id="state"
                        name="state"
                        placeholder="BY"
                        value={searchData.state}
                        onChange={(e) => handleInputChange('state', e.target.value)}
                        required
                        autoComplete="off"
                      />
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="zipCode">Postleitzahl (Optional)</Label>
                      <Input
                        id="zipCode"
                        name="zipCode"
                        placeholder="80331"
                        value={searchData.zipCode}
                        onChange={(e) => handleInputChange('zipCode', e.target.value)}
                        autoComplete="off"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="maxResults">Maximale Ergebnisse</Label>
                      <Select
                        value={searchData.maxResults.toString()}
                        onValueChange={(value) => handleInputChange('maxResults', parseInt(value))}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="10">10 Ergebnisse</SelectItem>
                          <SelectItem value="20">20 Ergebnisse</SelectItem>
                          <SelectItem value="50">50 Ergebnisse</SelectItem>
                          <SelectItem value="100">100 Ergebnisse</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <Button 
                    type="submit" 
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-lg py-6"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                        Google Maps wird gescannt...
                      </>
                    ) : (
                      <>
                        <Search className="w-5 h-5 mr-2" />
                        Lead-Scraping starten
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* What You'll Get */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Was Sie erhalten</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Firmennamen & Adressen</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Telefonnummern & Websites</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Sterne-Bewertungen & Anzahl Rezensionen</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>E-Mail-Adressen (falls verfügbar)</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Exportierbares CSV-Format</span>
                </div>
              </CardContent>
            </Card>

            {/* Example Searches */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Beliebte Suchen</CardTitle>
                <CardDescription>
                  Probieren Sie diese Beispielsuchen aus, um zu starten
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {exampleSearches.map((example, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    className="w-full justify-start text-left"
                    onClick={() => setSearchData(prev => ({
                      ...prev,
                      query: example.query,
                      city: example.city,
                      state: example.state
                    }))}
                  >
                    <ArrowRight className="w-4 h-4 mr-2 text-gray-400" />
                    <div>
                      <div className="font-medium">{example.query}</div>
                      <div className="text-xs text-gray-500">{example.city}, {example.state}</div>
                    </div>
                  </Button>
                ))}
              </CardContent>
            </Card>

            {/* Pricing Info */}
            <Card className="border-blue-200 bg-blue-50">
              <CardHeader>
                <CardTitle className="text-lg text-blue-800">Kostenlos testen</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-blue-700">
                <p className="mb-3">
                  Diese Demo verwendet Mock-Daten, um Ihnen genau zu zeigen, wie das System funktioniert.
                </p>
                <p>
                  In der Produktion kostet jede Suche etwa 0,02-0,10€, abhängig von den Ergebnissen.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
};

export default LeadScraper;