import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { MapPin, Search, Zap, Database, Mail, Star, Phone, Globe } from "lucide-react";

const Homepage = () => {
  const [email, setEmail] = useState("");
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate("/scraper");
  };

  const handleEmailSubmit = (e) => {
    e.preventDefault();
    alert("Thanks for subscribing! You'll get updates on new automation templates.");
    setEmail("");
  };

  const features = [
    {
      icon: <MapPin className="w-8 h-8 text-blue-600" />,
      title: "Google Maps Scraping",
      description: "Extract local business data from Google Maps automatically with precise location targeting."
    },
    {
      icon: <Database className="w-8 h-8 text-green-600" />,
      title: "Automated Data Collection",
      description: "Gather business names, addresses, phone numbers, websites, and ratings in seconds."
    },
    {
      icon: <Mail className="w-8 h-8 text-purple-600" />,
      title: "Email Enrichment", 
      description: "Automatically find missing email addresses using advanced contact discovery algorithms."
    },
    {
      icon: <Zap className="w-8 h-8 text-yellow-600" />,
      title: "Export Button Theory",
      description: "Turn manual data exports into automated workflows that save hours of repetitive work."
    }
  ];

  const useCases = [
    "Marketing Agencies - Generate leads for local businesses",
    "Sales Teams - Build prospect lists for outreach campaigns", 
    "Entrepreneurs - Research competitors and market opportunities",
    "Freelancers - Find potential clients in target industries"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Search className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold text-gray-900">LeadMaps</span>
          </div>
          <nav className="hidden md:flex gap-6">
            <Link to="/dashboard" className="text-gray-600 hover:text-blue-600 transition-colors">
              Dashboard
            </Link>
            <Link to="/scraper" className="text-gray-600 hover:text-blue-600 transition-colors">
              Scraper
            </Link>
            <Button onClick={handleGetStarted} className="bg-blue-600 hover:bg-blue-700">
              Get Started
            </Button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <Badge className="mb-6 bg-blue-100 text-blue-700 border-blue-200">
            🚀 Based on Greg Isenberg's Export Button Theory
          </Badge>
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Turn Google Maps Into Your
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              {" "}Lead Generation{" "}
            </span>
            Powerhouse
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
            Stop manually copying business information from Google Maps. Our AI-powered automation 
            extracts leads with phone numbers, emails, ratings, and contact details in seconds.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button 
              size="lg" 
              onClick={handleGetStarted}
              className="bg-blue-600 hover:bg-blue-700 text-lg px-8 py-3"
            >
              Start Scraping Leads
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              onClick={() => navigate("/dashboard")}
              className="text-lg px-8 py-3"
            >
              View Demo Results
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16">
          {[
            { number: "10,000+", label: "Leads Generated" },
            { number: "500+", label: "Happy Users" }, 
            { number: "95%", label: "Data Accuracy" },
            { number: "30s", label: "Average Scrape Time" }
          ].map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-3xl font-bold text-blue-600">{stat.number}</div>
              <div className="text-gray-600">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Features */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
            Powerful Lead Generation Features
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow border-gray-200">
                <CardHeader className="text-center pb-4">
                  <div className="mx-auto mb-4 p-3 bg-gray-50 rounded-full w-fit">
                    {feature.icon}
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-center">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* How It Works */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
            How It Works - The Export Button Theory in Action
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: "1",
                title: "Enter Your Search",
                description: "Type what you're looking for (e.g., 'restaurants in NYC') and set your parameters.",
                icon: <Search className="w-6 h-6" />
              },
              {
                step: "2", 
                title: "AI Scrapes Google Maps",
                description: "Our automation finds businesses, extracts contact info, ratings, and reviews automatically.",
                icon: <Zap className="w-6 h-6" />
              },
              {
                step: "3",
                title: "Export Clean Data",
                description: "Get organized spreadsheet with names, phones, emails, addresses ready for outreach.",
                icon: <Database className="w-6 h-6" />
              }
            ].map((step, index) => (
              <div key={index} className="text-center">
                <div className="mx-auto mb-4 w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold">
                  {step.step}
                </div>
                <h3 className="text-xl font-semibold mb-3 text-gray-900">{step.title}</h3>
                <p className="text-gray-600">{step.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Use Cases */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
            Perfect For These Use Cases
          </h2>
          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {useCases.map((useCase, index) => (
              <div key={index} className="flex items-center gap-3 p-4 bg-white rounded-lg border border-gray-200">
                <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                <span className="text-gray-700">{useCase}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Newsletter Signup */}
        <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
          <div className="text-center mb-6">
            <h3 className="text-2xl font-bold text-gray-900 mb-3">
              Get More Automation Blueprints
            </h3>
            <p className="text-gray-600">
              Join 5,000+ entrepreneurs getting weekly automation ideas and templates based on the Export Button Theory.
            </p>
          </div>
          <form onSubmit={handleEmailSubmit} className="flex gap-3 max-w-md mx-auto">
            <Input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="flex-1"
              required
            />
            <Button type="submit" className="bg-blue-600 hover:bg-blue-700">
              Subscribe
            </Button>
          </form>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 mt-16">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Search className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold">LeadMaps</span>
          </div>
          <p className="text-gray-400 mb-6">
            Automated lead generation powered by the Export Button Theory
          </p>
          <div className="flex justify-center gap-6">
            <Link to="/dashboard" className="text-gray-400 hover:text-white transition-colors">
              Dashboard
            </Link>
            <Link to="/scraper" className="text-gray-400 hover:text-white transition-colors">
              Lead Scraper
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Homepage;