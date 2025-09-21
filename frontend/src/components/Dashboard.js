import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { 
  Search, 
  TrendingUp, 
  Users, 
  Database, 
  MapPin, 
  Star, 
  Clock,
  ArrowUpRight,
  Download,
  Plus
} from "lucide-react";
import { mockScrapeResults } from "../data/mockScrapeResults";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const navigate = useNavigate();
  
  const recentSearches = [
    {
      id: 1,
      query: "restaurants in New York, NY",
      results: 20,
      date: "2 hours ago",
      avgRating: 4.3
    },
    {
      id: 2, 
      query: "plumbers in Austin, TX",
      results: 15,
      date: "1 day ago",
      avgRating: 4.1
    },
    {
      id: 3,
      query: "hair salons in Los Angeles, CA", 
      results: 25,
      date: "3 days ago",
      avgRating: 4.5
    }
  ];

  const stats = {
    totalLeads: 2847,
    totalSearches: 156,
    avgConversion: 23.4,
    emailsEnriched: 1429
  };

  const topPerformingSearches = [
    {
      query: "Italian restaurants",
      location: "NYC",
      leads: 45,
      emailRate: 78
    },
    {
      query: "Auto repair shops", 
      location: "Chicago",
      leads: 32,
      emailRate: 65
    },
    {
      query: "Dental clinics",
      location: "Miami", 
      leads: 28,
      emailRate: 82
    }
  ];

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
            <Button variant="outline" onClick={() => navigate('/results')}>
              View Results
            </Button>
            <Button onClick={() => navigate('/scraper')} className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              New Search
            </Button>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Header Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Lead Generation Dashboard
          </h1>
          <p className="text-gray-600">
            Track your Google Maps scraping performance and manage your leads
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Leads</CardTitle>
              <Database className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalLeads.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                <span className="text-green-600 flex items-center gap-1">
                  <ArrowUpRight className="w-3 h-3" />
                  +12% from last month
                </span>
              </p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Searches</CardTitle>
              <Search className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalSearches}</div>
              <p className="text-xs text-muted-foreground">
                <span className="text-green-600 flex items-center gap-1">
                  <ArrowUpRight className="w-3 h-3" />
                  +8% from last month
                </span>
              </p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Conversion Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.avgConversion}%</div>
              <p className="text-xs text-muted-foreground">
                <span className="text-green-600 flex items-center gap-1">
                  <ArrowUpRight className="w-3 h-3" />
                  +2.1% from last month
                </span>
              </p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Emails Found</CardTitle>
              <Users className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.emailsEnriched.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                <span className="text-green-600 flex items-center gap-1">
                  <ArrowUpRight className="w-3 h-3" />
                  +18% from last month
                </span>
              </p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="recent" className="w-full">
          <TabsList className="grid w-full grid-cols-3 max-w-md">
            <TabsTrigger value="recent">Recent Searches</TabsTrigger>
            <TabsTrigger value="top">Top Performing</TabsTrigger>
            <TabsTrigger value="demo">Demo Data</TabsTrigger>
          </TabsList>
          
          <TabsContent value="recent" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Recent Lead Searches
                  <Button size="sm" onClick={() => navigate('/scraper')}>
                    <Plus className="w-4 h-4 mr-1" />
                    New Search
                  </Button>
                </CardTitle>
                <CardDescription>
                  Your latest Google Maps scraping activities
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentSearches.map((search) => (
                    <div key={search.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                          <MapPin className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <h3 className="font-medium text-gray-900">{search.query}</h3>
                          <div className="flex items-center gap-4 text-sm text-gray-500">
                            <span className="flex items-center gap-1">
                              <Database className="w-3 h-3" />
                              {search.results} results
                            </span>
                            <span className="flex items-center gap-1">
                              <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                              {search.avgRating} avg
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {search.date}
                            </span>
                          </div>
                        </div>
                      </div>
                      <Button size="sm" variant="outline">
                        View Results
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="top" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Top Performing Searches</CardTitle>
                <CardDescription>
                  Searches with the highest lead quality and email discovery rates
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {topPerformingSearches.map((search, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-4">
                        <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center text-sm font-bold text-green-600">
                          #{index + 1}
                        </div>
                        <div>
                          <h3 className="font-medium text-gray-900">{search.query}</h3>
                          <p className="text-sm text-gray-500">{search.location}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-6 text-sm">
                        <div className="text-center">
                          <div className="font-semibold text-blue-600">{search.leads}</div>
                          <div className="text-gray-500">Leads</div>
                        </div>
                        <div className="text-center">
                          <div className="font-semibold text-green-600">{search.emailRate}%</div>
                          <div className="text-gray-500">Email Rate</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="demo" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Demo Search Results
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" onClick={() => navigate('/results')}>
                      View Full Results
                    </Button>
                    <Button size="sm" className="bg-green-600 hover:bg-green-700">
                      <Download className="w-4 h-4 mr-1" />
                      Export CSV
                    </Button>
                  </div>
                </CardTitle>
                <CardDescription>
                  Sample data showing restaurants in New York, NY - {mockScrapeResults.length} results found
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {mockScrapeResults.slice(0, 5).map((result, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                          <MapPin className="w-4 h-4 text-orange-600" />
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">{result.businessName}</h4>
                          <div className="flex items-center gap-3 text-sm text-gray-500">
                            <Badge variant="secondary" className="text-xs">{result.businessType}</Badge>
                            {result.rating && (
                              <span className="flex items-center gap-1">
                                <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                                {result.rating} ({result.reviewCount})
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        {result.phone && <Badge variant="outline" className="text-green-600">Phone</Badge>}
                        {result.email && <Badge variant="outline" className="text-purple-600">Email</Badge>}
                        {result.website && <Badge variant="outline" className="text-blue-600">Website</Badge>}
                      </div>
                    </div>
                  ))}
                  
                  <div className="pt-4 text-center">
                    <Button onClick={() => navigate('/results')} className="bg-blue-600 hover:bg-blue-700">
                      View All {mockScrapeResults.length} Results
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Quick Actions */}
        <div className="mt-8">
          <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
            <CardHeader>
              <CardTitle className="text-blue-800">Ready to Find More Leads?</CardTitle>
              <CardDescription className="text-blue-600">
                Start a new Google Maps search and discover potential customers in seconds
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col sm:flex-row gap-3">
                <Button onClick={() => navigate('/scraper')} className="bg-blue-600 hover:bg-blue-700">
                  <Search className="w-4 h-4 mr-2" />
                  Start New Search
                </Button>
                <Button variant="outline" onClick={() => navigate('/results')}>
                  View Demo Results
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;