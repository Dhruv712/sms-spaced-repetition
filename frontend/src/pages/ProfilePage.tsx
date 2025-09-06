import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { buildApiUrl } from '../config';

interface UserProfile {
  name: string;
  phone_number: string;
  study_mode: string;
  preferred_start_hour: number;
  preferred_end_hour: number;
  timezone: string;
  sms_opt_in: boolean;
}

const ProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [countryCode, setCountryCode] = useState('+1');
  const [phoneNumber, setPhoneNumber] = useState('');
  const { token } = useAuth();

  useEffect(() => {
    if (!token) return;

    axios.get(buildApiUrl('/users/profile'), {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
      .then(res => {
        setProfile(res.data);
        // Parse phone number if it exists
        if (res.data.phone_number) {
          const phone = res.data.phone_number;
          // Extract country code (assume it starts with +)
          const match = phone.match(/^(\+\d{1,4})(.*)$/);
          if (match) {
            setCountryCode(match[1]);
            setPhoneNumber(match[2]);
          } else {
            setPhoneNumber(phone);
          }
        }
      })
      .catch(err => {
        console.error("Failed to fetch profile", err);
        setError('Failed to load profile. Please try again.');
      });
  }, [token]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    if (!profile) return;
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  const handleSave = async () => {
    if (!profile || !token) return;
    setIsSaving(true);
    setError('');
    setMessage('');

    try {
      // Combine country code and phone number - SIMPLE LOGIC
      const fullPhoneNumber = phoneNumber.trim() ? `${countryCode}${phoneNumber.replace(/\D/g, '')}` : '';
      
      const profileData = {
        ...profile,
        phone_number: fullPhoneNumber
      };

      await axios.put(buildApiUrl('/users/profile'), profileData, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setMessage('Profile saved successfully!');
    } catch (err) {
      console.error('Failed to save profile:', err);
      setError('Failed to save profile. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  if (!profile) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-darkbg">
        <div className="text-xl text-gray-600 dark:text-gray-300">Loading profile...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 bg-gray-50 dark:bg-darkbg min-h-screen">
      <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-darktext">User Profile</h1>

      <div className="bg-white dark:bg-darksurface rounded-lg shadow-xl p-8 max-w-2xl mx-auto border border-gray-200 dark:border-gray-700">
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200 rounded-md">
            {error}
          </div>
        )}
        {message && (
          <div className="mb-4 p-3 bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-200 rounded-md">
            {message}
          </div>
        )}

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name</label>
            <input
              name="name"
              value={profile.name}
              onChange={handleChange}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:text-darktext dark:border-gray-600 transition-colors duration-200"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Phone Number</label>
            <div className="flex gap-2">
              <select
                value={countryCode}
                onChange={(e) => setCountryCode(e.target.value)}
                className="w-24 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:text-darktext dark:border-gray-600 appearance-none"
              >
                <option value="+1">🇺🇸 +1</option>
                <option value="+44">🇬🇧 +44</option>
                <option value="+33">🇫🇷 +33</option>
                <option value="+49">🇩🇪 +49</option>
                <option value="+81">🇯🇵 +81</option>
                <option value="+86">🇨🇳 +86</option>
                <option value="+91">🇮🇳 +91</option>
                <option value="+61">🇦🇺 +61</option>
                <option value="+55">🇧🇷 +55</option>
                <option value="+52">🇲🇽 +52</option>
                <option value="+39">🇮🇹 +39</option>
                <option value="+34">🇪🇸 +34</option>
                <option value="+31">🇳🇱 +31</option>
                <option value="+46">🇸🇪 +46</option>
                <option value="+47">🇳🇴 +47</option>
                <option value="+45">🇩🇰 +45</option>
                <option value="+41">🇨🇭 +41</option>
                <option value="+43">🇦🇹 +43</option>
                <option value="+32">🇧🇪 +32</option>
                <option value="+351">🇵🇹 +351</option>
                <option value="+30">🇬🇷 +30</option>
                <option value="+48">🇵🇱 +48</option>
                <option value="+420">🇨🇿 +420</option>
                <option value="+36">🇭🇺 +36</option>
                <option value="+40">🇷🇴 +40</option>
                <option value="+359">🇧🇬 +359</option>
                <option value="+385">🇭🇷 +385</option>
                <option value="+386">🇸🇮 +386</option>
                <option value="+421">🇸🇰 +421</option>
                <option value="+370">🇱🇹 +370</option>
                <option value="+371">🇱🇻 +371</option>
                <option value="+372">🇪🇪 +372</option>
                <option value="+7">🇷🇺 +7</option>
                <option value="+380">🇺🇦 +380</option>
                <option value="+375">🇧🇾 +375</option>
                <option value="+90">🇹🇷 +90</option>
                <option value="+20">🇪🇬 +20</option>
                <option value="+27">🇿🇦 +27</option>
                <option value="+234">🇳🇬 +234</option>
                <option value="+254">🇰🇪 +254</option>
                <option value="+233">🇬🇭 +233</option>
                <option value="+212">🇲🇦 +212</option>
                <option value="+213">🇩🇿 +213</option>
                <option value="+216">🇹🇳 +216</option>
                <option value="+218">🇱🇾 +218</option>
                <option value="+220">🇬🇲 +220</option>
                <option value="+221">🇸🇳 +221</option>
                <option value="+222">🇲🇷 +222</option>
                <option value="+223">🇲🇱 +223</option>
                <option value="+224">🇬🇳 +224</option>
                <option value="+225">🇨🇮 +225</option>
                <option value="+226">🇧🇫 +226</option>
                <option value="+227">🇳🇪 +227</option>
                <option value="+228">🇹🇬 +228</option>
                <option value="+229">🇧🇯 +229</option>
                <option value="+230">🇲🇺 +230</option>
                <option value="+231">🇱🇷 +231</option>
                <option value="+232">🇸🇱 +232</option>
                <option value="+235">🇹🇩 +235</option>
                <option value="+236">🇨🇫 +236</option>
                <option value="+237">🇨🇲 +237</option>
                <option value="+238">🇨🇻 +238</option>
                <option value="+239">🇸🇹 +239</option>
                <option value="+240">🇬🇶 +240</option>
                <option value="+241">🇬🇦 +241</option>
                <option value="+242">🇨🇬 +242</option>
                <option value="+243">🇨🇩 +243</option>
                <option value="+244">🇦🇴 +244</option>
                <option value="+245">🇬🇼 +245</option>
                <option value="+246">🇮🇴 +246</option>
                <option value="+247">🇦🇨 +247</option>
                <option value="+248">🇸🇨 +248</option>
                <option value="+249">🇸🇩 +249</option>
                <option value="+250">🇷🇼 +250</option>
                <option value="+251">🇪🇹 +251</option>
                <option value="+252">🇸🇴 +252</option>
                <option value="+253">🇩🇯 +253</option>
                <option value="+255">🇹🇿 +255</option>
                <option value="+256">🇺🇬 +256</option>
                <option value="+257">🇧🇮 +257</option>
                <option value="+258">🇲🇿 +258</option>
                <option value="+260">🇿🇲 +260</option>
                <option value="+261">🇲🇬 +261</option>
                <option value="+262">🇷🇪 +262</option>
                <option value="+263">🇿🇼 +263</option>
                <option value="+264">🇳🇦 +264</option>
                <option value="+265">🇲🇼 +265</option>
                <option value="+266">🇱🇸 +266</option>
                <option value="+267">🇧🇼 +267</option>
                <option value="+268">🇸🇿 +268</option>
                <option value="+269">🇰🇲 +269</option>
                <option value="+290">🇸🇭 +290</option>
                <option value="+291">🇪🇷 +291</option>
                <option value="+297">🇦🇼 +297</option>
                <option value="+298">🇫🇴 +298</option>
                <option value="+299">🇬🇱 +299</option>
                <option value="+350">🇬🇮 +350</option>
                <option value="+351">🇵🇹 +351</option>
                <option value="+352">🇱🇺 +352</option>
                <option value="+353">🇮🇪 +353</option>
                <option value="+354">🇮🇸 +354</option>
                <option value="+355">🇦🇱 +355</option>
                <option value="+356">🇲🇹 +356</option>
                <option value="+357">🇨🇾 +357</option>
                <option value="+358">🇫🇮 +358</option>
                <option value="+359">🇧🇬 +359</option>
                <option value="+370">🇱🇹 +370</option>
                <option value="+371">🇱🇻 +371</option>
                <option value="+372">🇪🇪 +372</option>
                <option value="+373">🇲🇩 +373</option>
                <option value="+374">🇦🇲 +374</option>
                <option value="+375">🇧🇾 +375</option>
                <option value="+376">🇦🇩 +376</option>
                <option value="+377">🇲🇨 +377</option>
                <option value="+378">🇸🇲 +378</option>
                <option value="+380">🇺🇦 +380</option>
                <option value="+381">🇷🇸 +381</option>
                <option value="+382">🇲🇪 +382</option>
                <option value="+383">🇽🇰 +383</option>
                <option value="+385">🇭🇷 +385</option>
                <option value="+386">🇸🇮 +386</option>
                <option value="+387">🇧🇦 +387</option>
                <option value="+389">🇲🇰 +389</option>
                <option value="+390">🇻🇦 +390</option>
                <option value="+420">🇨🇿 +420</option>
                <option value="+421">🇸🇰 +421</option>
                <option value="+423">🇱🇮 +423</option>
                <option value="+500">🇫🇰 +500</option>
                <option value="+501">🇧🇿 +501</option>
                <option value="+502">🇬🇹 +502</option>
                <option value="+503">🇸🇻 +503</option>
                <option value="+504">🇭🇳 +504</option>
                <option value="+505">🇳🇮 +505</option>
                <option value="+506">🇨🇷 +506</option>
                <option value="+507">🇵🇦 +507</option>
                <option value="+508">🇵🇲 +508</option>
                <option value="+509">🇭🇹 +509</option>
                <option value="+590">🇬🇵 +590</option>
                <option value="+591">🇧🇴 +591</option>
                <option value="+592">🇬🇾 +592</option>
                <option value="+593">🇪🇨 +593</option>
                <option value="+594">🇬🇫 +594</option>
                <option value="+595">🇵🇾 +595</option>
                <option value="+596">🇲🇶 +596</option>
                <option value="+597">🇸🇷 +597</option>
                <option value="+598">🇺🇾 +598</option>
                <option value="+599">🇧🇶 +599</option>
                <option value="+670">🇹🇱 +670</option>
                <option value="+672">🇦🇶 +672</option>
                <option value="+673">🇧🇳 +673</option>
                <option value="+674">🇳🇷 +674</option>
                <option value="+675">🇵🇬 +675</option>
                <option value="+676">🇹🇴 +676</option>
                <option value="+677">🇸🇧 +677</option>
                <option value="+678">🇻🇺 +678</option>
                <option value="+679">🇫🇯 +679</option>
                <option value="+680">🇵🇼 +680</option>
                <option value="+681">🇼🇫 +681</option>
                <option value="+682">🇨🇰 +682</option>
                <option value="+683">🇳🇺 +683</option>
                <option value="+684">🇦🇸 +684</option>
                <option value="+685">🇼🇸 +685</option>
                <option value="+686">🇰🇮 +686</option>
                <option value="+687">🇳🇨 +687</option>
                <option value="+688">🇹🇻 +688</option>
                <option value="+689">🇵🇫 +689</option>
                <option value="+690">🇹🇰 +690</option>
                <option value="+691">🇫🇲 +691</option>
                <option value="+692">🇲🇭 +692</option>
                <option value="+850">🇰🇵 +850</option>
                <option value="+852">🇭🇰 +852</option>
                <option value="+853">🇲🇴 +853</option>
                <option value="+855">🇰🇭 +855</option>
                <option value="+856">🇱🇦 +856</option>
                <option value="+880">🇧🇩 +880</option>
                <option value="+886">🇹🇼 +886</option>
                <option value="+960">🇲🇻 +960</option>
                <option value="+961">🇱🇧 +961</option>
                <option value="+962">🇯🇴 +962</option>
                <option value="+963">🇸🇾 +963</option>
                <option value="+964">🇮🇶 +964</option>
                <option value="+965">🇰🇼 +965</option>
                <option value="+966">🇸🇦 +966</option>
                <option value="+967">🇾🇪 +967</option>
                <option value="+968">🇴🇲 +968</option>
                <option value="+970">🇵🇸 +970</option>
                <option value="+971">🇦🇪 +971</option>
                <option value="+972">🇮🇱 +972</option>
                <option value="+973">🇧🇭 +973</option>
                <option value="+974">🇶🇦 +974</option>
                <option value="+975">🇧🇹 +975</option>
                <option value="+976">🇲🇳 +976</option>
                <option value="+977">🇳🇵 +977</option>
                <option value="+992">🇹🇯 +992</option>
                <option value="+993">🇹🇲 +993</option>
                <option value="+994">🇦🇿 +994</option>
                <option value="+995">🇬🇪 +995</option>
                <option value="+996">🇰🇬 +996</option>
                <option value="+998">🇺🇿 +998</option>
              </select>
              <input
                type="tel"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="1234567890"
                className="flex-1 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:text-darktext dark:border-gray-600 transition-colors duration-200"
              />
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Add your phone number to receive SMS flashcard reminders and use text-based features.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Study Mode</label>
            <select
              name="study_mode"
              value={profile.study_mode}
              onChange={handleChange}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:text-darktext dark:border-gray-600 appearance-none pr-8 transition-colors duration-200"
            >
              <option value="batch">Batch</option>
              <option value="distributed">Distributed</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Start Hour (24-hour format)</label>
            <input
              type="number"
              name="preferred_start_hour"
              value={profile.preferred_start_hour}
              onChange={handleChange}
              min="0"
              max="23"
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:text-darktext dark:border-gray-600 transition-colors duration-200"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">End Hour (24-hour format)</label>
            <input
              type="number"
              name="preferred_end_hour"
              value={profile.preferred_end_hour}
              onChange={handleChange}
              min="0"
              max="23"
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:text-darktext dark:border-gray-600 transition-colors duration-200"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Timezone</label>
            <input
              name="timezone"
              value={profile.timezone}
              onChange={handleChange}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:text-darktext dark:border-gray-600 transition-colors duration-200"
            />
          </div>

          <div className="flex items-center">
            <input
              id="sms-opt-in"
              name="sms_opt_in"
              type="checkbox"
              checked={profile.sms_opt_in}
              onChange={(e) => setProfile({ ...profile, sms_opt_in: e.target.checked })}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded dark:bg-gray-700 dark:border-gray-600 dark:checked:bg-primary-600 dark:checked:border-primary-600"
            />
            <label htmlFor="sms-opt-in" className="ml-2 block text-sm text-gray-900 dark:text-darktext">
              <span className="font-medium">Receive SMS notifications</span>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Get daily flashcard reminders and spaced repetition notifications via text message.
              </p>
            </label>
          </div>

          <button
            onClick={handleSave}
            disabled={isSaving}
            className="w-full px-4 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200"
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
