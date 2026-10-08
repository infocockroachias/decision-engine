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
        <Navigation currentPage="profile" />
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
        <Navigation currentPage="profile" />
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
      <Navigation currentPage="profile" />
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
                  <div key={point.month} className="flex items-center justify-between">
                    <span className="text-sm text-slate-600">{point.month}</span>
                    <span className="text-sm font-semibold text-slate-900">{point.accuracy}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Strong & Weak Areas */}
        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="mb-4 text-lg font-semibold text-green-700">💪 Strong Areas</h3>
            <div className="space-y-3">
              {profile.strongAreas.map((area) => (
                <div key={area.topic} className="flex items-center justify-between">
                  <span className="text-sm text-slate-700">{area.topic}</span>
                  <span className="text-sm font-semibold text-green-600">{area.accuracy}%</span>
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="mb-4 text-lg font-semibold text-red-700">🎯 Areas to Improve</h3>
            <div className="space-y-3">
              {profile.weakAreas.map((area) => (
                <div key={area.topic} className="flex items-center justify-between">
                  <span className="text-sm text-slate-700">{area.topic}</span>
                  <span className="text-sm font-semibold text-red-600">{area.accuracy}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="mt-8">
          <h2 className="text-xl font-semibold text-slate-900 mb-4">Recent Activity</h2>
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="space-y-3">
              {profile.recentActivity.map((activity, i) => (
                <div key={i} className="flex items-center justify-between border-b border-slate-100 pb-3 last:border-0">
                  <div>
                    <p className="text-sm font-medium text-slate-900">{activity.action}</p>
                    <p className="text-xs text-slate-500">{activity.details}</p>
                  </div>
                  <span className="text-xs text-slate-400">{activity.date}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
