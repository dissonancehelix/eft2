public sealed class SpawnPoint : Component
{
	[Property] public TeamId Team { get; set; } = TeamId.None;
	[Property] public int Index { get; set; }
}
