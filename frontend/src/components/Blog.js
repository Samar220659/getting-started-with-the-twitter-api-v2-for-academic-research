import React from "react";
import { Link } from "react-router-dom";
import { mockData } from "../data/mock";

const Blog = () => {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="flex justify-between items-center px-8 py-6">
        <Link to="/" className="text-2xl font-bold handwritten-style">
          GREG ISENBERG
        </Link>
        <nav className="flex gap-8">
          <Link to="/blog" className="text-black font-medium">
            Blog
          </Link>
          <Link to="/about-me" className="text-gray-700 hover:text-black transition-colors">
            About Me
          </Link>
        </nav>
      </header>

      {/* Blog Content */}
      <main className="max-w-4xl mx-auto px-8 py-8">
        <h1 className="text-5xl font-bold mb-12">Blog</h1>
        
        <div className="space-y-12">
          {mockData.blogPosts.map((post) => (
            <article key={post.id} className="border-b border-gray-200 pb-8">
              <h2 className="text-2xl font-semibold mb-4">
                <a href="#" className="hover:underline">{post.title}</a>
              </h2>
              <p className="text-gray-600 mb-4">{post.excerpt}</p>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span>{post.date}</span>
                <span>•</span>
                <span>{post.readTime} min read</span>
              </div>
            </article>
          ))}
        </div>
      </main>
    </div>
  );
};

export default Blog;