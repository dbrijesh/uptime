import React, { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const GovernanceSlides = () => {
  const [currentSlide, setCurrentSlide] = useState(0);

  const slides = [
    {
      title: "AI Coding Tools - Unified Governance Framework",
      subtitle: "Comparative Capabilities: GitHub Copilot | Claude Code | Cursor IDE",
      unified: true,
      sections: [
        {
          title: "Access & Governance",
          color: "bg-orange-50",
          rows: [
            {
              category: "Centralized Control",
              copilot: "Admin controls via GitHub organization settings. Enable/disable for entire org, specific users, or teams.",
              claude: "Access governed by Anthropic API key policies and usage limits. Team management tied to Anthropic account structure.",
              cursor: "Project & model-level control. Configure which LLM provider (OpenAI, Anthropic, Azure) per project. Cursor Teams subscription."
            },
            {
              category: "SSO Integration",
              copilot: "Enterprise SSO (SAML 2.0/OAuth). Integrates with AWS IAM Identity Center, Okta, Azure AD.",
              claude: "SSO integration depends on Anthropic platform's enterprise features. SAML/OIDC support for Business+ plans.",
              cursor: "SAML SSO available. User and group management through Teams admin console."
            },
            {
              category: "Policy Enforcement",
              copilot: "ADMX/ADML Group Policies. Content exclusions at repository/organization level. Disable Agent Mode.",
              claude: "MCP server controls with allowlist/denylist. Domain capture for auto workspace enrollment. RBAC roles.",
              cursor: "Rules file version control. Model access configuration. Can enforce local models (Ollama) for air-gapped development."
            }
          ]
        },
        {
          title: "Usage Monitoring & Controls",
          color: "bg-blue-50",
          rows: [
            {
              category: "Usage Reporting",
              copilot: "Organization owners view aggregate metrics (suggestions accepted/rejected). 30-day audit log retention.",
              claude: "Compliance API for real-time usage data. Usage and cost metrics in Anthropic developer console.",
              cursor: "Local-first privacy mode available. Monitoring relies on chosen LLM provider's logs and network egress controls."
            },
            {
              category: "Spending Controls",
              copilot: "Set spending limits per organization. Per-seat pricing model with clear cost attribution.",
              claude: "Usage budgets and alerts in console. Org & user-level spend limits. Granular cost-per-task tracking.",
              cursor: "Provider-dependent cost tracking. Requires integration with AI Gateway (Portkey) for unified monitoring."
            },
            {
              category: "Audit & Compliance",
              copilot: "Logs integrate with AWS CloudTrail for API call auditing. GitHub Advanced Security integration.",
              claude: "Custom integration with monitoring tools (CloudWatch, Datadog). Session activity logs exportable to SIEM.",
              cursor: "Completely Local Mode prevents code from leaving machine. Telemetry limited when using cloud models."
            }
          ]
        },
        {
          title: "Security Controls",
          color: "bg-green-50",
          rows: [
            {
              category: "Data Protection",
              copilot: "Private Code Assurance: GitHub does not use customer code to train models (Business+ plans). Code referencing filter.",
              claude: "Zero Data Retention (ZDR) option. No training on customer data. SOC 2 Type II certified.",
              cursor: "Guardrails feature auto-redacts sensitive data (keys, emails) from prompts. Privacy mode blocks cloud transmission."
            },
            {
              category: "Code Security",
              copilot: "Built-in filter avoids suggesting public matching code. Pre-commit hook integration for secret scanning.",
              claude: "In-context security via prompt validation. Content sanitization before API calls. Command blocklist (curl, wget).",
              cursor: "Configurable to block code execution from Agent. Local execution ensures code runs on user machine only."
            },
            {
              category: "Network Security",
              copilot: "Content exclusions prevent sensitive files from being available to Copilot. VNet integration via Azure OpenAI.",
              claude: "Sandboxed execution in isolated VM environments. Permission system requires explicit approval for file access.",
              cursor: "MCP Server Control allows only allowlisted internal servers. Can enforce air-gapped local models (Ollama)."
            }
          ]
        },
        {
          title: "LLM Usage Metrics",
          color: "bg-purple-50",
          rows: [
            {
              category: "Productivity Metrics",
              copilot: "Acceptance rate, total suggestions, lines of code suggested. Tied to developer productivity and cost-per-developer.",
              claude: "Lines accepted per session. Code generation rate. Error detection and security issue flagging.",
              cursor: "Tab completion stats. Suggestion acceptance tracking. Metrics derived from backend provider (OpenAI, Anthropic)."
            },
            {
              category: "Cost Analytics",
              copilot: "Per-seat model ($19-39/month). Language distribution metrics. Usage tied to license allocation.",
              claude: "Token-based analytics (input/output tokens per request). Cost-per-task efficiency analysis. 500K context window tracking.",
              cursor: "Provider-dependent pricing. Key metric: cloud vs. local model usage ratio impacting data residency costs."
            },
            {
              category: "Performance Tracking",
              copilot: "Response time monitoring. Model performance metrics. Suggestions shown vs. accepted ratio.",
              claude: "Context window utilization. Agentic action usage (plan, read, write operations). Latency per API call.",
              cursor: "Model selection impact analysis. Can measure agentic action usage. Multi-provider performance comparison."
            }
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
            { name: "GitHub Copilot", score: 95, note: "Mature admin controls, extensive documentation" },
            { name: "Claude Code", score: 90, note: "Strong compliance API, enterprise SSO" },
            { name: "Cursor IDE", score: 70, note: "Manual configuration, limited native controls" }
          ]
        },
        {
          name: "Built-in Monitoring",
          tools: [
            { name: "GitHub Copilot", score: 85, note: "Native analytics dashboard" },
            { name: "Claude Code", score: 95, note: "Compliance API + console metrics" },
            { name: "Cursor IDE", score: 50, note: "Requires external gateway integration" }
          ]
        },
        {
          name: "Security Controls",
          tools: [
            { name: "GitHub Copilot", score: 90, note: "Content exclusions + referencing filter" },
            { name: "Claude Code", score: 95, note: "ZDR, sandboxed execution, permissions" },
            { name: "Cursor IDE", score: 85, note: "Guardrails + local-first privacy mode" }
          ]
        },
        {
          name: "Cost Visibility",
          tools: [
            { name: "GitHub Copilot", score: 80, note: "Simple per-seat model" },
            { name: "Claude Code", score: 90, note: "Granular token-based tracking" },
            { name: "Cursor IDE", score: 60, note: "Provider-dependent, requires gateway" }
          ]
        }
      ]
    },
    {
      title: "Implementation Roadmap",
      subtitle: "45-Day Phased Deployment Approach",
      timeline: true,
      phases: [
        {
          phase: "Phase 1: Assessment & Foundation",
          duration: "Week 1-2",
          color: "bg-blue-50 border-blue-400",
          tasks: [
            "Inventory current AI tool usage and shadow IT across development teams",
            "Define data classification policies (public, internal, confidential, restricted)",
            "Select and configure SSO provider (AWS IAM Identity Center, Okta, Azure AD)",
            "Establish baseline security requirements and compliance frameworks (SOC 2, ISO 27001)",
            "Calculate ROI: Investment vs. prevented incidents (£500/user/year vs. £50K/incident)"
          ]
        },
        {
          phase: "Phase 2: Pilot Deployment",
          duration: "Week 3-4",
          color: "bg-green-50 border-green-400",
          tasks: [
            "Deploy to IT/Security team (20-50 pilot users) for validation",
            "Configure content exclusions, privacy modes, and guardrails for sensitive repositories",
            "Enable audit logging, integrate with SIEM (Splunk, CloudWatch, Datadog)",
            "Document access request and approval workflows",
            "Implement pre-commit hooks for secret scanning (gitleaks, semgrep)"
          ]
        },
        {
          phase: "Phase 3: Scale & Monitor",
          duration: "Week 5-8",
          color: "bg-purple-50 border-purple-400",
          tasks: [
            "Gradual rollout to development teams by department (25% → 50% → 100%)",
            "Deploy AI Gateway (Kong, Portkey) for unified policy enforcement across tools",
            "Set up cost attribution, usage alerts, and chargeback models per team",
            "Train developers on secure coding practices and AI tool limitations",
            "Establish incident response procedures for AI-related security events"
          ]
        },
        {
          phase: "Phase 4: Optimization & Governance",
          duration: "Ongoing",
          color: "bg-orange-50 border-orange-400",
          tasks: [
            "Review LLM usage metrics monthly: acceptance rates, cost trends, anomaly detection",
            "Refine policies based on incident analysis and user feedback",
            "Automate compliance reporting (quarterly audits, license compliance scans)",
            "Continuous improvement: update content exclusions, tune rate limits, optimize costs",
            "Expand governance to new AI tools (Tabnine, CodeWhisperer, Cursor extensions)"
          ]
        }
      ]
    },
    {
      title: "Best Practices & Reference Architecture",
      subtitle: "Zero Trust AI Security Framework",
      bestPractices: true,
      sections: [
        {
          category: "Zero Trust Architecture",
          icon: "🔐",
          practices: [
            "Never trust, always verify: Treat AI-generated code like external contributions",
            "Implement API-based access over web interfaces (10x more secure per industry research)",
            "Route all AI traffic through centralized AI Gateway with DLP scanning",
            "Apply principle of least privilege: Grant minimum necessary model/feature access",
            "Isolate sensitive repositories with content exclusions and air-gapped local models"
          ]
        },
        {
          category: "Data Protection & Privacy",
          icon: "🛡️",
          practices: [
            "Enable privacy modes by default: GitHub Private Code, Claude ZDR, Cursor Local Mode",
            "Configure content exclusions for confidential code (financial algorithms, auth logic)",
            "Strip PII/secrets from prompts automatically using guardrails and input validation",
            "Use Zero Data Retention (ZDR) for GDPR/HIPAA regulated environments",
            "Implement data residency controls: Azure OpenAI VNet, on-prem models via Ollama"
          ]
        },
        {
          category: "Continuous Monitoring & Compliance",
          icon: "📊",
          practices: [
            "Track acceptance rates to detect anomalies: Sudden drops may indicate quality/security issues",
            "Monitor token consumption vs. budget limits with automated alerts (90% threshold)",
            "Alert on unusual access patterns: Off-hours usage, unfamiliar locations, data exfiltration attempts",
            "Integrate audit logs into SIEM: Correlate AI tool usage with security events",
            "Quarterly compliance audits: License scanning, policy violations, cost optimization reviews"
          ]
        },
        {
          category: "Developer Training & Culture",
          icon: "👥",
          practices: [
            "Educate on prompt injection, supply chain risks, and adversarial examples",
            "Code review AI-generated code with same rigor as peer contributions",
            "Enforce pre-commit hooks: Secret scanning (gitleaks), vulnerability detection (semgrep)",
            "Treat AI tools as untrusted junior developers: Always validate suggestions",
            "Foster a culture of responsible AI use: Report suspicious behavior, share lessons learned"
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
      <div className="bg-gradient-to-r from-blue-900 to-blue-700 text-white p-5 shadow-lg">
        <h1 className="text-2xl font-bold">{currentSlideData.title}</h1>
        <p className="text-blue-100 mt-1 text-sm">{currentSlideData.subtitle}</p>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto p-4">
        {/* Unified Tabular Slide */}
        {currentSlideData.unified && (
          <div className="space-y-4 max-w-7xl mx-auto">
            {currentSlideData.sections.map((section, idx) => (
              <div key={idx} className={`${section.color} border-2 border-gray-300 rounded-lg shadow-lg overflow-hidden`}>
                <div className="bg-gradient-to-r from-gray-700 to-gray-600 text-white p-3">
                  <h3 className="text-lg font-bold">{section.title}</h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="bg-gray-200 border-b-2 border-gray-400">
                        <th className="p-2 text-left font-bold text-gray-800 w-32">Category</th>
                        <th className="p-2 text-left font-bold text-blue-700 border-l-2 border-gray-300">GitHub Copilot</th>
                        <th className="p-2 text-left font-bold text-purple-700 border-l-2 border-gray-300">Claude Code</th>
                        <th className="p-2 text-left font-bold text-green-700 border-l-2 border-gray-300">Cursor IDE</th>
                      </tr>
                    </thead>
                    <tbody>
                      {section.rows.map((row, rowIdx) => (
                        <tr key={rowIdx} className={`border-b border-gray-300 ${rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                          <td className="p-2 font-semibold text-gray-700 align-top">{row.category}</td>
                          <td className="p-2 text-gray-700 border-l-2 border-gray-300 align-top">{row.copilot}</td>
                          <td className="p-2 text-gray-700 border-l-2 border-gray-300 align-top">{row.claude}</td>
                          <td className="p-2 text-gray-700 border-l-2 border-gray-300 align-top">{row.cursor}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Comparison Slide */}
        {currentSlideData.comparison && (
          <div className="max-w-6xl mx-auto">
            <div className="space-y-6">
              {currentSlideData.categories.map((category, idx) => (
                <div key={idx} className="bg-white rounded-lg p-5 shadow-lg border-2 border-gray-200">
                  <h3 className="text-xl font-bold mb-3 text-gray-800">{category.name}</h3>
                  <div className="space-y-3">
                    {category.tools.map((tool, toolIdx) => (
                      <div key={toolIdx} className="flex items-center gap-3">
                        <div className="w-36 font-semibold text-gray-700 text-sm">{tool.name}</div>
                        <div className="flex-1 bg-gray-100 rounded-full h-7 relative">
                          <div
                            className="bg-gradient-to-r from-blue-500 to-blue-600 h-7 rounded-full flex items-center justify-end pr-2 text-white font-bold text-xs transition-all duration-500"
                            style={{ width: `${tool.score}%` }}
                          >
                            {tool.score}%
                          </div>
                        </div>
                        <div className="w-52 text-xs text-gray-600 italic">{tool.note}</div>
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
          <div className="max-w-6xl mx-auto">
            <div className="space-y-4">
              {currentSlideData.phases.map((phase, idx) => (
                <div key={idx} className={`${phase.color} border-2 rounded-lg p-4 shadow-md`}>
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-bold text-gray-800">{phase.phase}</h3>
                    <span className="bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-semibold">
                      {phase.duration}
                    </span>
                  </div>
                  <ul className="space-y-1.5">
                    {phase.tasks.map((task, taskIdx) => (
                      <li key={taskIdx} className="flex items-start text-sm">
                        <span className="text-blue-600 mr-2 mt-0.5 font-bold">✓</span>
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
            <div className="grid grid-cols-2 gap-5">
              {currentSlideData.sections.map((section, idx) => (
                <div key={idx} className="bg-white border-2 border-gray-200 rounded-lg p-5 shadow-lg">
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-3xl">{section.icon}</span>
                    <h3 className="text-lg font-bold text-gray-800">{section.category}</h3>
                  </div>
                  <ul className="space-y-2">
                    {section.practices.map((practice, practiceIdx) => (
                      <li key={practiceIdx} className="flex items-start">
                        <span className="text-green-600 mr-2 mt-0.5 font-bold">•</span>
                        <span className="text-gray-700 text-xs leading-relaxed">{practice}</span>
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
      <div className="bg-white border-t-2 border-gray-200 p-3 shadow-lg">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <button
            onClick={prevSlide}
            className="flex items-center gap-2 px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold text-sm"
          >
            <ChevronLeft size={18} />
            Previous
          </button>
          
          <div className="flex items-center gap-2">
            <span className="text-gray-600 font-semibold text-sm">
              Slide {currentSlide + 1} of {slides.length}
            </span>
            <div className="flex gap-2 ml-4">
              {slides.map((_, idx) => (
                <button
                  key={idx}
                  onClick={() => setCurrentSlide(idx)}
                  className={`w-2.5 h-2.5 rounded-full transition-all ${
                    idx === currentSlide ? 'bg-blue-600 w-7' : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>
          </div>

          <button
            onClick={nextSlide}
            className="flex items-center gap-2 px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold text-sm"
          >
            Next
            <ChevronRight size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default GovernanceSlides;
