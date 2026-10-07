"use client";

import { useState, useEffect } from "react";
import Navigation from "@/components/Navigation";
import ScoreCard from "@/components/ScoreCard";
import SubjectPieChart from "@/components/SubjectPieChart";
import FocusArea from "@/components/FocusArea";
import RecommendationList from "@/components/RecommendationList";

interface ProfileData {
  name: string;
  email: string;
  joinDate: string;
  testsCompleted: number;
  totalQuestions: number;
  avgAccuracy: number;
  strongAreas: { topic: string; accuracy: number }[];
  weakAreas: { topic: string; accuracy: number }[];
  improvementTrend: { month: string; accuracy: number }[];
  subjectPerformance: { name: string; correct: number; wrong: number; skipped: number; color: string }[];
  recentActivity: { date: string; action: string; details: string }[];
}

export default function ProfilePage() {
  const [currentPage, setCurrentPage] = useState("profile");
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchProfile() {
      try {
        const res = await fetch("/api/profile");
        if (!res.ok) throw new Error("Failed to fetch profile data");
        const data = await res.json();
        setProfile(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }
    fetchProfile();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navigation currentPage={currentPage} onNavigate={setCurrentPage} />
        <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center min-h-[60vh]">
            <div className="text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-brand/30 border-t-brand" />
              <p className="mt-4 text-sm text-slate-500">Loading profile...</p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navigation currentPage={currentPage} onNavigate={setCurrentPage} />
        <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center">
            <p className="text-red-700 font-medium">{error || "Profile not found"}</p>
          </div>
        </main>
      </div>
    );
  }

  const trendDirection = profile.improvementTrend.length >= 2
    ? profile.improvementTrend[profile.improvementTrend.length - 1].accuracy - profile.improvementTrend[0].accuracy
    : 0;

  return (
    <div className="min-h-screen bg-slate-50">
      <Navigation currentPage={currentPage} onNavigate={setCurrentPage} />
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Profile Header */}
        <div className="mb-8 flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand text-white text-2xl font-bold">
            {profile.name.charAt(0)}
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">{profile.name}</h1>
            <p className="text-sm text-slate-500">{profile.email} · Member since {profile.joinDate}</p>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
          <ScoreCard label="Tests Completed" value={profile.testsCompleted} />
          <ScoreCard label="Questions Attempted" value={profile.totalQuestions} />
          <ScoreCard label="Avg Accuracy" value={`${profile.avgAccuracy}%`} variant="correct" />
          <ScoreCard label="Improvement" value={`${trendDirection >= 0 ? "+" : ""}${trendDirection}%`} variant={trendDirection >= 0 ? "correct" : "wrong"} sublabel="Since starting" />
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Subject Performance */}
          <div className="lg:col-span-2">
            <SubjectPieChart data={profile.subjectPerformance} title="Overall Subject Performance" />
          </div>

          {/* Improvement Trend */}
          <div className="lg:col-span-1">
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="mb-4 text-lg font-semibold text-slate-900">Improvement Trend</h3>
              <div className="space-y-3">
                {profile.improvementTrend.map((point) => (
                  <div key={point.month} className="flex items-center gap-3">
                    <span className="text-xs text-slate-500 w-12">{point.month}</span>
                    <div className="flex-1 h-3 rounded-full bg-slate-100 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-brand transition-all duration-500"
                        style={{ width: `${point.accuracy}%` }}
                      />
                    </div>
                    <span className="text-sm font-semibold text-slate-700 w-10 text-right">{point.accuracy}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Strong & Weak Areas */}
        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          {/* Strong Areas */}
          <div>
            <h3 className="mb-4 text-lg font-semibold text-green-700 flex items-center gap-2">
              <span>💪</span> Strong Areas
            </h3>
            <div className="space-y-3">
              {profile.strongAreas.length > 0 ? (
                profile.strongAreas.map((area) => (
                  <FocusArea
                    key={area.topic}
                    topic={area.topic}
                    accuracy={area.accuracy}
                    questionsAttempted={0}
                    trend="improving"
                  />
                ))
              ) : (
                <p className="text-sm text-slate-400 text-center py-4">Complete more tests to identify strong areas</p>
              )}
            </div>
          </div>

          {/* Weak Areas */}
          <div>
            <h3 className="mb-4 text-lg font-semibold text-red-700 flex items-center gap-2">
              <span>📈</span> Areas to Improve
            </h3>
            <div className="space-y-3">
              {profile.weakAreas.length > 0 ? (
                profile.weakAreas.map((area) => (
                  <FocusArea
                    key={area.topic}
                    topic={area.topic}
                    accuracy={area.accuracy}
                    questionsAttempted={0}
                    trend="declining"
                  />
                ))
              ) : (
                <p className="text-sm text-slate-400 text-center py-4">Complete more tests to identify weak areas</p>
              )}
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div className="mt-8">
          <RecommendationList
            recommendations={[
              ...profile.weakAreas.slice(0, 3).map((area, i) => ({
                id: `weak-${i}`,
                type: "improvement" as const,
                title: `Improve ${area.topic}`,
                description: `Your accuracy in ${area.topic} is ${area.accuracy}%. Focus on NCERT books and practice more questions from this area.`,
                priority: "high" as const,
                subject: area.topic,
              })),
            ]}
          />
        </div>

        {/* Recent Activity */}
        <div className="mt-8">
          <h3 className="mb-4 text-lg font-semibold text-slate-900">Recent Activity</h3>
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="space-y-4">
              {profile.recentActivity.map((activity, i) => (
                <div key={i} className="flex items-start gap-3 border-b border-slate-100 pb-3 last:border-0 last:pb-0">
                  <div className="h-2 w-2 mt-2 rounded-full bg-brand flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-sm text-slate-700">{activity.action}</p>
                    <p className="text-xs text-slate-400">{activity.details}</p>
                  </div>
                  <span className="text-xs text-slate-400 flex-shrink-0">{activity.date}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}