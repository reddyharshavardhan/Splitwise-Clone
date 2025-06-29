import React, { useState } from 'react';

function GroupForm() {
  const [name, setName] = useState('');
  const [userIds, setUserIds] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    await fetch('http://localhost:8000/groups', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        name,
        user_ids: userIds.split(',').map(Number),
      }),
    });
    setName('');
    setUserIds('');
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 max-w-md mx-auto">
      <input value={name} onChange={e => setName(e.target.value)} className="border p-2 m-2" placeholder="Group Name" />
      <input value={userIds} onChange={e => setUserIds(e.target.value)} className="border p-2 m-2" placeholder="User IDs (comma-separated)" />
      <button type="submit" className="bg-blue-500 text-white p-2 rounded">Create Group</button>
    </form>
  );
}

export default GroupForm;