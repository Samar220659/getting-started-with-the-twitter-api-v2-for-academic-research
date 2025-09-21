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
    alert("Danke für die Anmeldung! Sie erhalten Updates zu neuen Automatisierungsvorlagen.");
    setEmail("");
  };

  const features = [
    {
      icon: <MapPin className="w-8 h-8 text-blue-600" />,
      title: "Google Maps Scraping",
      description: "Extrahieren Sie automatisch lokale Unternehmensdaten von Google Maps mit präziser Standortzielgruppenadressierung."
    },
    {
      icon: <Database className="w-8 h-8 text-green-600" />,
      title: "Automatisierte Datensammlung",
      description: "Sammeln Sie Firmennamen, Adressen, Telefonnummern, Websites und Bewertungen in Sekunden."
    },
    {
      icon: <Mail className="w-8 h-8 text-purple-600" />,
      title: "E-Mail-Anreicherung", 
      description: "Finden Sie automatisch fehlende E-Mail-Adressen mit fortschrittlichen Kontaktentdeckungsalgorithmen."
    },
    {
      icon: <Zap className="w-8 h-8 text-yellow-600" />,
      title: "Export-Button-Theorie",
      description: "Verwandeln Sie manuelle Datenexporte in automatisierte Workflows, die stundenlange Wiederholungsarbeit sparen."
    }
  ];

  const useCases = [
    "Marketing-Agenturen - Generieren Sie Leads für lokale Unternehmen",
    "Vertriebsteams - Erstellen Sie Prospect-Listen für Outreach-Kampagnen", 
    "Unternehmer - Recherchieren Sie Konkurrenten und Marktmöglichkeiten",
    "Freiberufler - Finden Sie potenzielle Kunden in Zielbranchen"
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
              Jetzt starten
            </Button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <Badge className="mb-6 bg-blue-100 text-blue-700 border-blue-200">
            🚀 Basierend auf Greg Isenbergs Export-Button-Theorie
          </Badge>
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Verwandeln Sie Google Maps in Ihr
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              {" "}Lead-Generierungs{" "}
            </span>
            Kraftwerk
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
            Hören Sie auf, Unternehmensinformationen manuell von Google Maps zu kopieren. Unsere KI-gestützte Automatisierung 
            extrahiert Leads mit Telefonnummern, E-Mails, Bewertungen und Kontaktdaten in Sekunden.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button 
              size="lg" 
              onClick={handleGetStarted}
              className="bg-blue-600 hover:bg-blue-700 text-lg px-8 py-3"
            >
              Leads scrapen starten
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              onClick={() => navigate("/dashboard")}
              className="text-lg px-8 py-3"
            >
              Demo-Ergebnisse anzeigen
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16">
          {[
            { number: "10.000+", label: "Generierte Leads" },
            { number: "500+", label: "Zufriedene Nutzer" }, 
            { number: "95%", label: "Datengenauigkeit" },
            { number: "30s", label: "Durchschnittliche Scrape-Zeit" }
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
            Kraftvolle Lead-Generierungs-Features
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
            So funktioniert es - Die Export-Button-Theorie in Aktion
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: "1",
                title: "Suchparameter eingeben",
                description: "Geben Sie ein, wonach Sie suchen (z.B. 'Restaurants in München') und legen Sie Ihre Parameter fest.",
                icon: <Search className="w-6 h-6" />
              },
              {
                step: "2", 
                title: "KI scant Google Maps",
                description: "Unsere Automatisierung findet Unternehmen und extrahiert automatisch Kontaktinformationen, Bewertungen und Rezensionen.",
                icon: <Zap className="w-6 h-6" />
              },
              {
                step: "3",
                title: "Saubere Daten exportieren",
                description: "Erhalten Sie eine organisierte Tabellenkalkulation mit Namen, Telefonnummern, E-Mails und Adressen für Ihre Kampagnen.",
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
            Perfekt für diese Anwendungsfälle
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
              Weitere Automatisierungs-Blueprints erhalten
            </h3>
            <p className="text-gray-600">
              Schließen Sie sich 5.000+ Unternehmern an, die wöchentliche Automatisierungsideen und Vorlagen basierend auf der Export-Button-Theorie erhalten.
            </p>
          </div>
          <form onSubmit={handleEmailSubmit} className="flex gap-3 max-w-md mx-auto">
            <Input
              type="email"
              placeholder="E-Mail-Adresse eingeben"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="flex-1"
              required
            />
            <Button type="submit" className="bg-blue-600 hover:bg-blue-700">
              Abonnieren
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
            Automatisierte Lead-Generierung basierend auf der Export-Button-Theorie
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