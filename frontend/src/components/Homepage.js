import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { mockData } from "../data/mock";

const Homepage = () => {
  const [email, setEmail] = useState("");

  const handleSubscribe = (e) => {
    e.preventDefault();
    alert("Thanks for subscribing! (This is a mock implementation)");
    setEmail("");
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="flex justify-between items-center px-8 py-6">
        <Link to="/" className="text-2xl font-bold handwritten-style">
          GREG ISENBERG
        </Link>
        <nav className="flex gap-8">
          <Link to="/blog" className="text-gray-700 hover:text-black transition-colors">
            Blog
          </Link>
          <Link to="/about-me" className="text-gray-700 hover:text-black transition-colors">
            About Me
          </Link>
        </nav>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
          {/* Left Column - Profile */}
          <div className="flex flex-col">
            <div className="mb-8">
              <img 
                src={mockData.profileImage} 
                alt="Greg Isenberg"
                className="w-20 h-20 rounded-full mb-6"
              />
              <div className="text-gray-600 leading-relaxed space-y-4">
                <p>
                  I'm the CEO of <a href="#" className="text-black underline hover:no-underline">Late Checkout</a> - a 
                  holding company building community-based internet businesses.
                </p>
                <p>
                  I've started and sold 3 venture-backed community companies. Now, I self-fund things.
                </p>
                <p>
                  I've been an advisor to companies like TikTok and Reddit.
                </p>
              </div>
            </div>

            <div>
              <p className="text-gray-500 mb-4">Find Me</p>
              <div className="flex gap-4">
                {mockData.socialLinks.map((link) => (
                  <a 
                    key={link.platform}
                    href={link.url} 
                    className="text-gray-400 hover:text-black transition-colors"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <link.icon className="w-5 h-5" />
                  </a>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column - Main Content */}
          <div className="flex flex-col">
            <div className="mb-12">
              <h1 className="text-6xl font-bold leading-tight mb-6">
                Startup ideas &<br />
                frameworks<br />
                <span className="bg-yellow-300 px-1">to help you win</span><br />
                on the internet.
              </h1>
              
              <div className="text-gray-600 leading-relaxed mb-8">
                <p className="mb-4">
                  I write a weekly letter called <strong>Greg's Letter</strong>. It's jam-packed 
                  with free startup ideas, insights on business building and ways to win in an internet world.
                </p>
                <p className="mb-6">
                  <strong>{mockData.subscriberCount}+</strong> people enjoy reading it. You probably will too.
                </p>
                <p>
                  You can subscribe below to get access to <strong>Greg's Letter</strong>
                </p>
              </div>

              <form onSubmit={handleSubscribe} className="flex gap-2 mb-6">
                <Input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="flex-1 bg-gray-100 border-none"
                  required
                />
                <Button type="submit" className="bg-black text-white hover:bg-gray-800">
                  Subscribe
                </Button>
              </form>

              <p className="text-yellow-600 font-semibold">
                <span className="text-2xl">{mockData.ideasCount}+</span> free startup ideas given since 2020
              </p>
            </div>

            {/* Popular Guides */}
            <div className="mb-12">
              <h3 className="text-gray-500 mb-6">Popular guides</h3>
              <div className="space-y-6">
                {mockData.popularGuides.map((guide, index) => (
                  <div key={index} className="border-l-2 border-gray-200 pl-6">
                    <h4 className="font-semibold text-lg mb-2 handwritten-style">
                      <a href="#" className="hover:underline">{guide.title}</a>
                    </h4>
                    <p className="text-gray-600 text-sm">{guide.description}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Podcast Section */}
            <div className="mb-12">
              <h3 className="text-gray-500 mb-6">Listen to my podcast</h3>
              <div className="bg-gray-50 p-6 rounded-lg">
                <h4 className="font-semibold mb-2">{mockData.latestPodcast.title}</h4>
                <p className="text-gray-600 text-sm mb-4">{mockData.latestPodcast.description}</p>
                <div className="flex gap-4">
                  <Button variant="outline" className="text-sm">
                    Play on Spotify
                  </Button>
                  <Button variant="outline" className="text-sm">
                    Youtube
                  </Button>
                  <Button variant="outline" className="text-sm">
                    Apple Podcasts
                  </Button>
                </div>
              </div>
            </div>

            {/* Portfolio Companies */}
            <div className="mb-12">
              <h3 className="text-gray-500 mb-6">Work with me and my team</h3>
              <p className="text-gray-600 mb-6">Check out my portfolio companies</p>
              <div className="grid grid-cols-1 gap-4">
                {mockData.portfolioCompanies.map((company, index) => (
                  <a 
                    key={index}
                    href="#" 
                    className="flex items-center gap-4 p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
                  >
                    <img 
                      src={company.logo} 
                      alt={company.name}
                      className="w-12 h-12 object-contain"
                    />
                    <div>
                      <h4 className="font-semibold">{company.name}</h4>
                      <p className="text-gray-600 text-sm">{company.description}</p>
                    </div>
                  </a>
                ))}
              </div>
            </div>

            {/* Social Links Footer */}
            <div>
              <h3 className="text-gray-500 mb-6">Find and follow me over here</h3>
              <div className="flex gap-6 mb-8">
                {mockData.socialLinks.map((link) => (
                  <a 
                    key={link.platform}
                    href={link.url}
                    className="text-gray-600 hover:text-black transition-colors"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {link.platform}
                  </a>
                ))}
              </div>
              <p className="text-gray-400 text-sm">©gregisenberg 2025</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Homepage;