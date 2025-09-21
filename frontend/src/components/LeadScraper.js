import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Badge } from "./ui/badge";
import { Search, MapPin, Loader2, ArrowRight, Zap, Download } from "lucide-react";
import { mockScrapeResults } from "../data/mockScrapeResults";

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
    
    // Simulate API call delay
    setTimeout(() => {
      // Store search data and navigate to results
      localStorage.setItem('lastSearch', JSON.stringify(searchData));
      localStorage.setItem('scrapeResults', JSON.stringify(mockScrapeResults));
      setIsLoading(false);
      navigate('/results');
    }, 3000);
  };

  const exampleSearches = [
    { query: "restaurants", city: "New York", state: "NY" },
    { query: "plumbers", city: "Austin", state: "TX" },
    { query: "hair salons", city: "Los Angeles", state: "CA" },
    { query: "gyms", city: "Miami", state: "FL" }
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
              <Link to="/dashboard">View Results</Link>
            </Button>
          </nav>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <Badge className="mb-4 bg-blue-100 text-blue-700 border-blue-200">
            <Zap className="w-4 h-4 mr-1" />
            Export Button Theory in Action
          </Badge>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Google Maps Lead Scraper
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Instead of manually copying data from Google Maps, let our automation do the work. 
            Get business details, contact info, and ratings in seconds.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Form */}
          <div className="lg:col-span-2">
            <Card className="shadow-lg border-0">
              <CardHeader className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-t-lg">
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="w-5 h-5" />
                  Lead Scraping Parameters
                </CardTitle>
                <CardDescription className="text-blue-100">
                  Configure your search to find the exact businesses you need
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <form onSubmit={handleScrape} className="space-y-6">
                  <div className="space-y-2">
                    <Label htmlFor="query" className="text-sm font-medium">
                      What are you looking for? *
                    </Label>
                    <Input
                      id="query"
                      placeholder="e.g., restaurants, plumbers, gyms, hair salons"
                      value={searchData.query}
                      onChange={(e) => handleInputChange('query', e.target.value)}
                      required
                      className="text-lg"
                    />
                    <p className="text-sm text-gray-500">
                      Be specific for better results (e.g., "Italian restaurants" vs "restaurants")
                    </p>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="city">City *</Label>
                      <Input
                        id="city"
                        placeholder="New York"
                        value={searchData.city}
                        onChange={(e) => handleInputChange('city', e.target.value)}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="state">State *</Label>
                      <Input
                        id="state"
                        placeholder="NY"
                        value={searchData.state}
                        onChange={(e) => handleInputChange('state', e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="zipCode">Zip Code (Optional)</Label>
                      <Input
                        id="zipCode"
                        placeholder="10001"
                        value={searchData.zipCode}
                        onChange={(e) => handleInputChange('zipCode', e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="maxResults">Maximum Results</Label>
                      <Select
                        value={searchData.maxResults.toString()}
                        onValueChange={(value) => handleInputChange('maxResults', parseInt(value))}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="10">10 results</SelectItem>
                          <SelectItem value="20">20 results</SelectItem>
                          <SelectItem value="50">50 results</SelectItem>
                          <SelectItem value="100">100 results</SelectItem>
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
                        Scraping Google Maps...
                      </>
                    ) : (
                      <>
                        <Search className="w-5 h-5 mr-2" />
                        Start Scraping Leads
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
                <CardTitle className="text-lg">What You'll Get</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Business names & addresses</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Phone numbers & websites</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Star ratings & review counts</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Email addresses (when available)</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Exportable CSV format</span>
                </div>
              </CardContent>
            </Card>

            {/* Example Searches */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Popular Searches</CardTitle>
                <CardDescription>
                  Try these example searches to get started
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
                <CardTitle className="text-lg text-blue-800">Free to Try</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-blue-700">
                <p className="mb-3">
                  This demo uses mock data to show you exactly how the system works.
                </p>
                <p>
                  In production, each search costs approximately $0.02-0.10 depending on results.
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