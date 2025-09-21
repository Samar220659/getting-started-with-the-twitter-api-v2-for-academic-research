import React from "react";
import { Link } from "react-router-dom";
import { mockData } from "../data/mock";

const About = () => {
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
          <Link to="/about-me" className="text-black font-medium">
            About Me
          </Link>
        </nav>
      </header>

      {/* About Content */}
      <main className="max-w-4xl mx-auto px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          <div className="lg:col-span-1">
            <img 
              src={mockData.profileImage} 
              alt="Greg Isenberg"
              className="w-48 h-48 rounded-full mb-8"
            />
          </div>
          
          <div className="lg:col-span-2">
            <h1 className="text-5xl font-bold mb-8">About Me</h1>
            
            <div className="text-gray-600 leading-relaxed space-y-6">
              <p className="text-xl">
                I'm the CEO of Late Checkout - a holding company building community-based internet businesses.
              </p>
              
              <p>
                I've started and sold 3 venture-backed community companies. Now, I self-fund things.
              </p>
              
              <p>
                I've been an advisor to companies like TikTok and Reddit, helping them navigate the complex world of online communities and product development.
              </p>
              
              <p>
                My passion lies in identifying opportunities in the digital landscape, particularly around community-driven businesses and AI automation. I believe the future belongs to entrepreneurs who can spot workflow breakdowns and turn them into profitable solutions.
              </p>
              
              <p>
                Through my weekly newsletter "Greg's Letter," I share startup ideas, frameworks, and insights with over 158,000+ entrepreneurs worldwide. My mission is to help ambitious builders create internet businesses that actually matter.
              </p>
              
              <p>
                When I'm not building or investing, you can find me sharing ideas on my podcast "The Startup Ideas Podcast" or helping entrepreneurs through my various portfolio companies.
              </p>
            </div>

            <div className="mt-12">
              <h3 className="text-xl font-semibold mb-4">Experience</h3>
              <div className="space-y-4">
                {mockData.experience.map((exp, index) => (
                  <div key={index} className="border-l-2 border-gray-200 pl-6">
                    <h4 className="font-semibold">{exp.role}</h4>
                    <p className="text-gray-600">{exp.company} • {exp.period}</p>
                    <p className="text-gray-600 text-sm mt-1">{exp.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default About;