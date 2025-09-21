import { Twitter, Youtube, Linkedin, Instagram } from "lucide-react";

export const mockData = {
  profileImage: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face&auto=format&q=80",
  
  subscriberCount: "158,485",
  ideasCount: "2122",
  
  socialLinks: [
    {
      platform: "Twitter",
      url: "https://twitter.com/gregisenberg",
      icon: Twitter
    },
    {
      platform: "Youtube", 
      url: "https://youtube.com/@GregIsenberg",
      icon: Youtube
    },
    {
      platform: "LinkedIn",
      url: "https://linkedin.com/in/gisenberg",
      icon: Linkedin
    },
    {
      platform: "Instagram",
      url: "https://instagram.com/gregisenberg", 
      icon: Instagram
    }
  ],

  popularGuides: [
    {
      title: "Find winning startup ideas using Reddit & AI",
      description: "My exact playbook for how to find internet gold on Reddit and use AI to find and validate startup ideas. (video tutorial included)"
    },
    {
      title: "The $500k Funnel Blueprint", 
      description: "The exact playbook to turn cold traffic into paying customers."
    },
    {
      title: "2 growth playbooks for your business",
      description: "Get a B2B & B2C growth playbooks to build your business."
    },
    {
      title: "AI Content Automation Guide",
      description: "Free vibe marketing workflow to automate your content and save 10+ hours a week."
    },
    {
      title: "Startup ideas bank (+ how I'd start them)",
      description: "A database with 30+ of my favorite startup ideas, collected from hundreds of conversations with top entrepreneurs."
    }
  ],

  latestPodcast: {
    title: "My n8n AI agent scrapes Google Maps and makes $$$",
    description: "In this episode, I dive deep into how I built an AI agent that automatically scrapes Google Maps data and turns it into recurring revenue."
  },

  portfolioCompanies: [
    {
      name: "Late Checkout",
      description: "A holding company for businesses powered by community",
      logo: "https://images.unsplash.com/photo-1560472355-536de3962603?w=50&h=50&fit=crop&auto=format&q=80"
    },
    {
      name: "Late Checkout Agency", 
      description: "The design (products, interfaces, agents) firm for the AI age",
      logo: "https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=50&h=50&fit=crop&auto=format&q=80"
    },
    {
      name: "Idea Browser",
      description: "The place to spot trends and startup ideas worth building", 
      logo: "https://images.unsplash.com/photo-1551033406-611cf9a28f67?w=50&h=50&fit=crop&auto=format&q=80"
    },
    {
      name: "The Vibe Marketer",
      description: "Automate boring marketing tasks with AI so you can vibe",
      logo: "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=50&h=50&fit=crop&auto=format&q=80"
    },
    {
      name: "Startup Empire",
      description: "Turn your ideas into income and build your internet empire",
      logo: "https://images.unsplash.com/photo-1558655146-d09347e92766?w=50&h=50&fit=crop&auto=format&q=80"
    }
  ],

  blogPosts: [
    {
      id: 1,
      title: "The Export Button Theory: Finding $30K/Month SaaS Opportunities",
      excerpt: "Every export button in enterprise software represents a workflow breakdown that could become a profitable AI SaaS business. Here's my framework for spotting these opportunities.",
      date: "Mar 15, 2024",
      readTime: 8
    },
    {
      id: 2,  
      title: "How I Built a $2M Community-Driven Business",
      excerpt: "The complete playbook for turning online communities into sustainable revenue streams, including the mistakes I made and lessons learned.",
      date: "Mar 8, 2024",
      readTime: 12
    },
    {
      id: 3,
      title: "AI Automation Opportunities Hiding in Plain Sight", 
      excerpt: "Manual processes in every industry are begging to be automated. Here's how to spot them and turn them into profitable micro-SaaS businesses.",
      date: "Feb 28, 2024", 
      readTime: 6
    },
    {
      id: 4,
      title: "The Reddit Gold Mine: Finding Startup Ideas in Comments",
      excerpt: "My systematic approach to mining Reddit for validated startup ideas, complete with tools and frameworks to identify pain points worth solving.",
      date: "Feb 20, 2024",
      readTime: 10
    },
    {
      id: 5,
      title: "Why I Stopped Taking VC Money (And You Should Too)",
      excerpt: "The hidden costs of venture capital and why bootstrapping your way to profitability might be the better path for most entrepreneurs.",
      date: "Feb 12, 2024", 
      readTime: 7
    }
  ],

  experience: [
    {
      role: "CEO & Founder",
      company: "Late Checkout",
      period: "2022 - Present",
      description: "Building a holding company of community-driven internet businesses focused on AI automation and workflow optimization."
    },
    {
      role: "Advisor", 
      company: "TikTok",
      period: "2020 - 2022",
      description: "Advised on community growth strategies and product development for creator tools and social commerce initiatives."
    },
    {
      role: "Advisor",
      company: "Reddit", 
      period: "2019 - 2021",
      description: "Consulted on community management best practices and helped develop strategies for monetizing niche communities."
    },
    {
      role: "Co-Founder & CEO",
      company: "Islands (Acquired)",
      period: "2018 - 2020", 
      description: "Built and sold a community platform that helped creators monetize their audiences through exclusive content and experiences."
    }
  ]
};