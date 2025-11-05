import React, { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const GovernanceSlides = () => {
  const [currentSlide, setCurrentSlide] = useState(0);

  const slides = [
    {
      title: "GitHub Copilot",
      subtitle: "Enterprise Governance Framework",
      sections: [
        {
          title: "Access & Governance",
          color: "bg-orange-100 border-orange-300",
          items: [
            { label: "SSO Integration", detail: "SAML 2.0 / OAuth" },
            { label: "Org-level Policies", detail: "Enable/disable per team" },
            { label: "Seat Management", detail: "Business/Enterprise licenses" },
            { label: "Content Exclusions", detail: "Repository/org-level filters" },
            { label: "Admin Templates", detail: "ADMX/ADML Group Policies" }
          ]
        },
        {
          title: "Usage Monitoring & Controls",
          color: "bg-blue-100 border-blue-300",
          items: [
            { label: "Usage Analytics", detail: "Acceptance rates & metrics" },
            { label: "Rate Limiting", detail: "Token limits per user/team" },
            { label: "Audit Logs", detail: "30-day retention in console" },
            { label: "Cost Attribution", detail: "Per-seat tracking" },
            { label: "Policy Enforcement", detail: "Preview features opt-in" }
          ]
        },
        {
          title: "Security Controls",
          color: "bg-green-100 border-green-300",
          items: [
            { label: "Code Completion Filter", detail: "Block passwords/secrets/keys" },
            { label: "No Training Guarantee", detail: "Business+ plans" },
            { label: "Content Scanning", detail: "Pre-commit hooks integration" },
            { label: "License Detection", detail: "Copyleft risk mitigation" },
            { label: "Agent Mode Control", detail: "Disable via Group Policy" }
          ]
        },
        {
          title: "LLM Usage Metrics",
          color: "bg-purple-100 border-purple-300",
          items: [
            { label: "Suggestions Shown", detail: "Count per developer" },
            { label: "Acceptance Rate", detail: "% of suggestions used" },
            { label: "Lines Generated", detail: "Total code produced" },
            { label: "Language Distribution", detail: "Per-language usage" },
            { label: "Model Performance", detail: "Response time tracking" }
          ]
        }
      ]
    },
    {
      title: "Claude Code",
      subtitle: "Enterprise Governance Framework",
      sections: [
        {
          title: "Access & Governance",
          color: "bg-orange-100 border-orange-300",
          items: [
            { label: "SAML/OIDC SSO", detail: "Okta, Azure AD, Ping" },
            { label: "RBAC Roles", detail: "Admin, Developer, Viewer" },
            { label: "Domain Capture", detail: "Auto workspace enrollment" },
            { label: "Premium Seats", detail: "Team & Enterprise plans" },
            { label: "MCP Server Controls", detail: "Allowlist/denylist configs" }
          ]
        },
        {
          title: "Usage Monitoring & Controls",
          color: "bg-blue-100 border-blue-300",
          items: [
            { label: "Compliance API", detail: "Real-time usage data" },
            { label: "Spend Controls", detail: "Org & user-level limits" },
            { label: "Usage Analytics", detail: "Lines accepted, accept rate" },
            { label: "Managed Policies", detail: "Tool permissions, file access" },
            { label: "Session Monitoring", detail: "Activity logs in SIEM" }
          ]
        },
        {
          title: "Security Controls",
          color: "bg-green-100 border-green-300",
          items: [
            { label: "Permission System", detail: "Explicit approval required" },
            { label: "Command Blocklist", detail: "Block curl, wget by default" },
            { label: "Zero Data Retention", detail: "Optional ZDR addendum" },
            { label: "SOC 2 Type II", detail: "Certified compliance" },
            { label: "Sandboxed Execution", detail: "Isolated VM environments" }
          ]
        },
        {
          title: "LLM Usage Metrics",
          color: "bg-purple-100 border-purple-300",
          items: [
            { label: "Token Consumption", detail: "Per user/team tracking" },
            { label: "Model Call Metadata", detail: "Without full prompts (ZDR)" },
            { label: "Code Generation Rate", detail: "Lines generated per session" },
            { label: "Error Detection", detail: "Bug/security issue flagging" },
            { label: "Context Window Usage", detail: "500K token tracking" }
          ]
        }
      ]
    },
    {
      title: "Cursor IDE",
      subtitle: "Enterprise Governance Framework",
      sections: [
        {
          title: "Access & Governance",
          color: "bg-orange-100 border-orange-300",
          items: [
            { label: "SAML SSO", detail: "Secure user access" },
            { label: "User/Group Mgmt", detail: "Create, update, remove" },
            { label: "Model Access Config", detail: "Control LLM provider access" },
            { label: "Privacy Mode", detail: "Must enable manually" },
            { label: "Rules File Controls", detail: "Version-controlled configs" }
          ]
        },
        {
          title: "Usage Monitoring & Controls",
          color: "bg-blue-100 border-blue-300",
          items: [
            { label: "Basic Logging", detail: "System performance telemetry" },
            { label: "No Native Audit Logs", detail: "Requires external tools" },
            { label: "Rate Limiting", detail: "Via AI Gateway integration" },
            { label: "Cost Tracking", detail: "Third-party monitoring needed" },
            { label: "Indexing Toggle", detail: "Disable codebase embeddings" }
          ]
        },
        {
          title: "Security Controls",
          color: "bg-green-100 border-green-300",
          items: [
            { label: "Privacy Mode", detail: "No persistent code storage" },
            { label: "SOC 2 Type II", detail: "Third-party certified" },
            { label: "Local Execution", detail: "Code runs on user machine" },
            { label: "Encryption", detail: "AES-256 at rest, TLS 1.2+" },
            { label: "MCP Server Review", detail: "Manual vetting required" }
          ]
        },
        {
          title: "LLM Usage Metrics",
          color: "bg-purple-100 border-purple-300",
          items: [
            { label: "Limited Telemetry", detail: "Optional data collection" },
            { label: "Suggestion Tracking", detail: "Tab completion stats" },
            { label: "Provider Metrics", detail: "OpenAI, Anthropic, Gemini" },
            { label: "Context Analysis", detail: "100-300 lines per request" },
            { label: "External Monitoring", detail: "Portkey/gateway integration" }
          ]
        }
      ]
    },
    {
      title: "Comparative Overview",
      subtitle: "AI Coding Tools Governance Maturity",
      comparison: true,
      categories: [
        {
          name: "Enterprise Readiness",
          tools: [
            { name: "GitHub Copilot", score: 95, note: "Mature admin controls" },
            { name: "Claude Code", score: 90, note: "Strong compliance focus" },
            { name: "Cursor IDE", score: 70, note: "Manual configuration heavy" }
          ]
        },
        {
          name: "Built-in Monitoring",
          tools: [
            { name: "GitHub Copilot", score: 85, note: "Native analytics" },
            { name: "Claude Code", score: 95, note: "Compliance API available" },
            { name: "Cursor IDE", score: 50, note: "Requires external tools" }
          ]
        },
        {
          name: "Security Controls",
          tools: [
            { name: "GitHub Copilot", score: 90, note: "Content exclusions" },
            { name: "Claude Code", score: 95, note: "Permission-based sandbox" },
            { name: "Cursor IDE", score: 85, note: "Privacy mode required" }
          ]
        },
        {
          name: "Cost Visibility",
          tools: [
            { name: "GitHub Copilot", score: 80, note: "Per-seat model clear" },
            { name: "Claude Code", score: 90, note: "Granular spend controls" },
            { name: "Cursor IDE", score: 60, note: "Gateway integration needed" }
          ]
        }
      ]
    },
    {
      title: "Implementation Roadmap",
      subtitle: "Phased Deployment Approach",
      timeline: true,
      phases: [
        {
          phase: "Phase 1: Foundation",
          duration: "Week 1-2",
          color: "bg-blue-50 border-blue-300",
          tasks: [
            "Inventory current AI tool usage across teams",
            "Define data classification & access policies",
            "Select SSO provider & configure authentication",
            "Establish baseline security requirements"
          ]
        },
        {
          phase: "Phase 2: Pilot Deployment",
          duration: "Week 3-4",
          color: "bg-green-50 border-green-300",
          tasks: [
            "Deploy to IT/Security team (20-50 users)",
            "Configure content exclusions & privacy modes",
            "Enable audit logging & monitoring dashboards",
            "Document access request procedures"
          ]
        },
        {
          phase: "Phase 3: Scale & Monitor",
          duration: "Week 5-8",
          color: "bg-purple-50 border-purple-300",
          tasks: [
            "Gradual rollout to development teams",
            "Implement AI Gateway for unified control",
            "Set up cost attribution & usage alerts",
            "Train developers on secure coding practices"
          ]
        },
        {
          phase: "Phase 4: Optimization",
          duration: "Ongoing",
          color: "bg-orange-50 border-orange-300",
          tasks: [
            "Review LLM usage metrics monthly",
            "Refine policies based on incident analysis",
            "Automate compliance reporting workflows",
            "Continuous improvement of guardrails"
          ]
        }
      ]
    },
    {
      title: "Best Practices",
      subtitle: "Securing AI Coding Tools at Scale",
      bestPractices: true,
      sections: [
        {
          category: "Zero Trust Architecture",
          icon: "🔐",
          practices: [
            "Never trust, always verify - even AI suggestions",
            "Implement API-based access over web interfaces",
            "Route all AI traffic through centralized gateway",
            "Apply principle of least privilege to tool permissions"
          ]
        },
        {
          category: "Data Protection",
          icon: "🛡️",
          practices: [
            "Enable privacy modes by default for sensitive repos",
            "Configure content exclusions for confidential code",
            "Strip PII/secrets from prompts automatically",
            "Use Zero Data Retention (ZDR) for regulated data"
          ]
        },
        {
          category: "Continuous Monitoring",
          icon: "📊",
          practices: [
            "Track acceptance rates to detect anomalies",
            "Monitor token consumption vs. budget limits",
            "Alert on unusual access patterns or data exfiltration",
            "Integrate audit logs into SIEM platforms"
          ]
        },
        {
          category: "Developer Training",
          icon: "👥",
          practices: [
            "Educate on prompt injection & supply chain risks",
            "Review AI-generated code like peer contributions",
            "Enforce pre-commit hooks for secret scanning",
            "Treat AI tools as untrusted junior developers"
          ]
        }
      ]
    }
  ];

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % slides.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);
  };

  const currentSlideData = slides[currentSlide];

  return (
    <div className="w-full h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex flex-col">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-900 to-blue-700 text-white p-6 shadow-lg">
        <h1 className="text-3xl font-bold">{currentSlideData.title}</h1>
        <p className="text-blue-100 mt-1">{currentSlideData.subtitle}</p>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto p-8">
        {/* Standard Slides */}
        {!currentSlideData.comparison && !currentSlideData.timeline && !currentSlideData.bestPractices && (
          <div className="grid grid-cols-2 gap-6 max-w-7xl mx-auto">
            {currentSlideData.sections.map((section, idx) => (
              <div key={idx} className={`${section.color} border-2 rounded-lg p-6 shadow-md`}>
                <h3 className="text-xl font-bold mb-4 text-gray-800 border-b-2 border-gray-300 pb-2">
                  {section.title}
                </h3>
                <div className="space-y-3">
                  {section.items.map((item, itemIdx) => (
                    <div key={itemIdx} className="flex flex-col">
                      <div className="flex items-start">
                        <span className="text-blue-600 mr-2 font-bold">▸</span>
                        <div>
                          <span className="font-semibold text-gray-800">{item.label}</span>
                          <p className="text-sm text-gray-600 ml-0">{item.detail}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Comparison Slide */}
        {currentSlideData.comparison && (
          <div className="max-w-6xl mx-auto">
            <div className="space-y-8">
              {currentSlideData.categories.map((category, idx) => (
                <div key={idx} className="bg-white rounded-lg p-6 shadow-lg border-2 border-gray-200">
                  <h3 className="text-2xl font-bold mb-4 text-gray-800">{category.name}</h3>
                  <div className="space-y-4">
                    {category.tools.map((tool, toolIdx) => (
                      <div key={toolIdx} className="flex items-center gap-4">
                        <div className="w-40 font-semibold text-gray-700">{tool.name}</div>
                        <div className="flex-1 bg-gray-100 rounded-full h-8 relative">
                          <div
                            className="bg-gradient-to-r from-blue-500 to-blue-600 h-8 rounded-full flex items-center justify-end pr-3 text-white font-bold text-sm transition-all duration-500"
                            style={{ width: `${tool.score}%` }}
                          >
                            {tool.score}%
                          </div>
                        </div>
                        <div className="w-48 text-sm text-gray-600 italic">{tool.note}</div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Timeline Slide */}
        {currentSlideData.timeline && (
          <div className="max-w-5xl mx-auto">
            <div className="space-y-6">
              {currentSlideData.phases.map((phase, idx) => (
                <div key={idx} className={`${phase.color} border-2 rounded-lg p-6 shadow-md`}>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold text-gray-800">{phase.phase}</h3>
                    <span className="bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                      {phase.duration}
                    </span>
                  </div>
                  <ul className="space-y-2">
                    {phase.tasks.map((task, taskIdx) => (
                      <li key={taskIdx} className="flex items-start">
                        <span className="text-blue-600 mr-2 mt-1">✓</span>
                        <span className="text-gray-700">{task}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Best Practices Slide */}
        {currentSlideData.bestPractices && (
          <div className="max-w-6xl mx-auto">
            <div className="grid grid-cols-2 gap-6">
              {currentSlideData.sections.map((section, idx) => (
                <div key={idx} className="bg-white border-2 border-gray-200 rounded-lg p-6 shadow-lg">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="text-4xl">{section.icon}</span>
                    <h3 className="text-xl font-bold text-gray-800">{section.category}</h3>
                  </div>
                  <ul className="space-y-3">
                    {section.practices.map((practice, practiceIdx) => (
                      <li key={practiceIdx} className="flex items-start">
                        <span className="text-green-600 mr-2 mt-1 font-bold">•</span>
                        <span className="text-gray-700 text-sm">{practice}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Navigation Footer */}
      <div className="bg-white border-t-2 border-gray-200 p-4 shadow-lg">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <button
            onClick={prevSlide}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            <ChevronLeft size={20} />
            Previous
          </button>
          
          <div className="flex items-center gap-2">
            <span className="text-gray-600 font-semibold">
              Slide {currentSlide + 1} of {slides.length}
            </span>
            <div className="flex gap-2 ml-4">
              {slides.map((_, idx) => (
                <button
                  key={idx}
                  onClick={() => setCurrentSlide(idx)}
                  className={`w-3 h-3 rounded-full transition-all ${
                    idx === currentSlide ? 'bg-blue-600 w-8' : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>
          </div>

          <button
            onClick={nextSlide}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            Next
            <ChevronRight size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default GovernanceSlides;